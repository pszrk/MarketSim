import asyncio
import json
import websockets
from orderbook import OrderBook
from simulate_orders import simulate_random_order

class WebSocketServer:
    def __init__(self, order_book):
        self.order_book = order_book
        self.websockets = set()
        self.server = None


    async def order_book_server(self, websocket, path):
        self.websockets.add(websocket)
        try:
            while True:
                await asyncio.sleep(1)  # Keep the connection open
        finally:
            self.websockets.remove(websocket)


    async def send_order_book_update(self, data):
        message = json.dumps(data)
        print(f"Sending message to client: {message}")
        # Use asyncio.gather to send the message to all connected clients concurrently
        asyncio.gather(*(websocket.send(message) for websocket in self.websockets))

    
    async def start_server(self):
        self.server = await websockets.serve(
            self.order_book_server,
            "localhost",
            5000
        )
        await self.server.wait_closed()

    async def stop_server(self):
        if self.server:
            print("trying to close server")
            self.server.close()
            await self.server.wait_closed()
        else: print("no server found")

async def run_simulation(server, delay):
    for _ in range(100):
        simulate_random_order(server.order_book, 1)
        order_book_status = server.order_book.get_status()
        print(f"status is {order_book_status}")
        await server.send_order_book_update(order_book_status)
        await(asyncio.sleep(delay))        


async def main():
    orderbook = OrderBook()
    srv = WebSocketServer(orderbook)
    server_task = asyncio.create_task(srv.start_server())
    simulation_task = asyncio.create_task(run_simulation(srv, 8))
    
    await simulation_task
    await srv.stop_server()

    # Use gather to await both tasks
    await asyncio.gather(server_task, simulation_task)


if __name__ == '__main__':
    asyncio.run(main()) 
