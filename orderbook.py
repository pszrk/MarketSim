import json

class Order:
    def __init__(self, side, price, quantity):
        self.side = side
        self.price = price
        self.quantity = quantity
    
    def __str__(self):
        return f"[{self.side};{self.price};{self.quantity}]."
    
    def to_dict(self):
        # Convert the Order object to a dictionary
        return {
            'side': self.side,
            'price': self.price,
            'quantity': self.quantity
        }


class OrderBook:
    def __init__(self):
        self.bids = {}  # dictionary with key: price, value: [list of orders]
        self.asks = {}
        self.price = 0

    def to_json_format(self):
        bids_data = [[price, sum(order.quantity for order in orders)] for price, orders in self.bids.items()]
        asks_data = [[price, sum(order.quantity for order in orders)] for price, orders in self.asks.items()]

        return {
            'price': self.price,
            'bids': bids_data,
            'asks': asks_data
        }
    
    def add_order(self, order):
        if order.side == 'buy':
            if order.price in self.bids:
                self.bids[order.price].append(order)
            else:
                self.bids[order.price] = [order]
        elif order.side == 'sell':
            if order.price in self.asks:
                self.asks[order.price].append(order)
            else:
                self.asks[order.price] = [order]
        self.match_orders(order)
    
    def match_orders(self, newest_order):
        for buy_price in sorted(self.bids.keys(), reverse=True):
            for sell_price in sorted(self.asks.keys()):
                if buy_price >= sell_price:
                    print(f"trying to match buy{buy_price} to sell{sell_price}")
                    matched_quantity = min(
                        sum(o.quantity for o in self.bids[buy_price]),
                        sum(o.quantity for o in self.asks[sell_price])
                    )
                    print(f" matched {matched_quantity}")
                    self.price = sell_price
                    self.execute_orders(self.bids[buy_price], matched_quantity)
                    self.execute_orders(self.asks[sell_price], matched_quantity)
                    if not self.bids[buy_price]:
                        print (f"removing bids key at {buy_price}")
                        del self.bids[buy_price]
                        if not self.asks[sell_price]:
                            print (f"also removing asks key at {sell_price}")
                            del self.asks[sell_price]
                        break
                    if not self.asks[sell_price]:
                        print (f"removing asks key at {sell_price}")
                        del self.asks[sell_price]
                        break
    
    def execute_orders(self, orders, quantity):
        remaining_quantity = quantity
        while remaining_quantity > 0 and orders:
            order = orders.pop(0)
            if order.quantity <= remaining_quantity:
                remaining_quantity -= order.quantity
            else:
                order.quantity -= remaining_quantity
                remaining_quantity = 0
                orders.insert(0, order)


    def process_order_update(self, add_or_remove, order):
        if add_or_remove == 'add':
            self.add_order(order)
        elif add_or_remove == 'remove':
            self.remove_order(order)
        return self


    def get_status(self):
        order_book_json = json.dumps(order_book.to_json_format(), indent=2)
        return order_book_json
    

def print_book(book):
    print("-------- Order Book: ------")
    for ask in book.asks:
        out = f"Sell Orders: {ask} "
        for o in book.asks[ask]:
            out += str(o)
        print(out)
    for bid in book.bids:
        out = f"Buy Orders: {bid} "
        for o in book.bids[bid]:
            out += str(o)
        print(out)
    print("---------------------------")

order_book = OrderBook()


print_book(order_book)