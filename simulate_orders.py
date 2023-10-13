import time
import random
from orderbook import OrderBook, Order

def generate_random_order():
    side = random.choice(['buy', 'sell'])
    price = round(random.uniform(45,50), 2)
    quantity = random.randint(1, 10)
    return Order(side, price, quantity)


def simulate_order_flow(order_book, num_orders, delay):
    for _ in range(num_orders):
        order = generate_random_order()
        print(f"Sending Order: {order.side} {order.quantity} @ {order.price}")
        order_book.process_order_update('add', order)        
        time.sleep(delay)


def simulate_random_order(order_book):
    order = generate_random_order()
    print(f"Sending Order: {order.side} {order.quantity} @ {order.price}")
    return order_book.process_order_update('add', order)


def send_custom_order(order_book, side, price, quantity):
    order = Order(side, price, quantity)
    print(f"sending custom order {side} {quantity} @ {price}")
    return order_book.process_order_update('add', order)



if __name__ == "__main__":
    order_book = OrderBook()

    simulate_order_flow(order_book, 10, 1)