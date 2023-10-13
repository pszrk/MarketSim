import asyncio
import json
import websockets
from websockets.exceptions import ConnectionClosedError
from orderbook import OrderBook
from simulate_orders import simulate_random_order

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
                await asyncio.sleep(1)  # Keep the connection open
        except ConnectionClosedError as e:
            print(f"Client disconnected: {e}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.websockets.remove(websocket)


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
    for _ in range(3):
        simulate_random_order(server.order_book)
        order_book_status = server.order_book.get_status()
        await server.send_order_book_update(order_book_status)
        await(asyncio.sleep(delay))        


async def main():
    orderbook = OrderBook()
    srv = WebSocketServer(orderbook)
    server_task = asyncio.create_task(srv.start_server())
    simulation_task = asyncio.create_task(run_server_simulation(srv, 8))
    
    await server_task
    await simulation_task
    await srv.stop_server()


if __name__ == '__main__':
    asyncio.run(main()) 
