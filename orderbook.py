class Order:
    def __init__(self, side, price, quantity):
        self.side = side
        self.price = price
        self.quantity = quantity
    
    def __str__(self):
        return f"[{self.side};{self.price};{self.quantity}]."


class OrderBook:
    def __init__(self):
        self.bids = {}  # dictionary with key: price, value: [list of orders]
        self.asks = {}
        self.price = 0
    
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
        self.match_orders()
    
    def match_orders(self):
        for buy_price in sorted(self.bids.keys(), reverse=True):
            for sell_price in sorted(self.asks.keys()):
                if buy_price >= sell_price:
                    matched_quantity = min(
                        sum(o.quantity for o in self.bids[buy_price]),
                        sum(o.quantity for o in self.asks[sell_price])
                    )
                    self.execute_orders(self.bids[buy_price], matched_quantity)
                    self.execute_orders(self.asks[sell_price], matched_quantity)
                    if not self.bids[buy_price]:
                        del self.bids[buy_price]
                    if not self.asks[sell_price]:
                        del self.asks[sell_price]
    
    def execute_orders(self, orders, quantity):
        remaining_quantity = quantity
        while remaining_quantity > 0 and orders:
            order = orders.pop(0)
            self.price = order.price
            if order.quantity <= remaining_quantity:
                remaining_quantity -= order.quantity
            else:
                order.quantity -= remaining_quantity
                remaining_quantity = 0
                orders.insert(0, order)
    
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


order_book.add_order(Order(side='buy', price=100.0, quantity=10))
order_book.add_order(Order(side='buy', price=99.5, quantity=5))
order_book.add_order(Order(side='buy', price=100.0, quantity=1))


order_book.add_order(Order(side='sell', price=101.0, quantity=8))
order_book.add_order(Order(side='sell', price=102.0, quantity=12))


print_book(order_book)

order_book.add_order(Order(side='buy', price=108.0, quantity=22))

print_book(order_book)
print("price:", order_book.price)
print("highest bid:", max((o for o in order_book.bids), default='n/a'))
print("lowest ask:", min((o for o in order_book.asks), default='n/a'))