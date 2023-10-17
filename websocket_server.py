import asyncio
import json
import websockets
from websockets.exceptions import ConnectionClosedError
from orderbook import OrderBook
from simulate_orders import simulate_random_order, send_custom_order

class WebSocketServer:
    def __init__(self, order_book):
        self.order_book = order_book
        self.websockets = set()
        self.server = None


    async def websocket_handler(self, websocket, path):
        self.websockets.add(websocket)
        print(f"added websocket {websocket}")
        try:
            while True:
                message = await websocket.recv()
                await self.process_received_message(message)
                if message is None:
                    break  # client has closed the connection
                else:
                    print(f"Received message from {websocket.remote_address}: {message}")
        except ConnectionClosedError as e:
            print(f"Client disconnected: {e}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.websockets.remove(websocket)


    def extract_order_data(message):
        try:
            # Parse the JSON string into a Python dictionary
            order_data = json.loads(message)

            price = order_data['price']
            amount = order_data['amount']
            side = order_data['side']

            return {
                'price': price,
                'amount': amount,
                'side': side
            }
        except json.JSONDecodeError:
            return None  # Return None if the message is not a valid JSON


    async def process_received_message(self, message):
        try:
            data = json.loads(message)
            # check if dictionary
            if isinstance(data, dict):
                if all(key in data and data[key] for key in ['price', 'amount', 'side']):
                    print("received message to submit custom order")
                    await self.submit_custom_order(
                        data['side'], int(data['price']), int(data['amount'])
                    )
                elif 'random' in data:
                    print("received message to generate random order")
                    await self.submit_random_order()
            else:
                print("unknown data format")
        except json.JSONDecodeError:
            print("message not in json format")

    
    async def submit_random_order(self):
        simulate_random_order(self.order_book)
        order_book_status = self.order_book.get_status()
        await self.send_order_book_update(order_book_status)


    async def submit_custom_order(self, side, price, quantity):
        try:
            if side not in {'buy', 'sell'} or \
                not int(quantity) or \
                not float(price):
                        print("incorrect data format in submit_custom_order, order discarded.") 
                        return
        except Exception as e:
            print("data format exception handled in submit_custom_order, order discarded.") 
            return
        
        send_custom_order(self.order_book, side, price, quantity)
        order_book_status = self.order_book.get_status()
        await self.send_order_book_update(order_book_status)


    async def disconnect_all(self):
        # disconnect all connected websockets
        for websocket in self.websockets:
            try:
                await websocket.close()
            except Exception as e:
                print(f"Error closing websocket: {e}")
        self.websockets.clear()


    async def send_order_book_update(self, data):
        message = json.dumps(data)
        #print(f"Sending message to client: {message}")
        # Use asyncio.gather to send the message to all connected clients concurrently
        asyncio.gather(*(websocket.send(message) for websocket in self.websockets))

    
    async def start_server(self):
        self.server = await websockets.serve(
            self.websocket_handler,
            "localhost", #0.0.0.0 = allow connections from any ip
            5000
        )
        print("server running")


    async def stop_server(self):        
        if self.server:
            print("trying to close server")
            try:
                await self.disconnect_all()
                print("websockets disconnected")
                if(self.server):
                    self.server.close()
                    await self.server.wait_closed()
                else:
                    print("not self server")
                print("all websockets disconnected and server closed")
            except Exception as e:
                print(f"an error occured during server close: {e}")
        else: print("no server found")



async def run_server_simulation(server, delay):
    for _ in range(50):
        simulate_random_order(server.order_book)
        order_book_status = server.order_book.get_status()
        await server.send_order_book_update(order_book_status)
        await(asyncio.sleep(delay))      


async def run_server_length():
    await(asyncio.sleep(600))


async def main():
    orderbook = OrderBook()
    srv = WebSocketServer(orderbook)
    server_task = asyncio.create_task(srv.start_server())
    #simulation_task = asyncio.create_task(run_server_simulation(srv, 8))
    server_uptime_task = asyncio.create_task(run_server_length())
    
    await server_task
    #await simulation_task
    await server_uptime_task
    await srv.stop_server()


if __name__ == '__main__':
    asyncio.run(main()) 
