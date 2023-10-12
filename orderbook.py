import json
from collections import deque

class Order:
    def __init__(self, side, price, quantity):
        self.side = side
        self.price = price
        self.quantity = quantity
    
    def __str__(self):
        return f"[{self.side};{self.price};{self.quantity}]."
    
    def to_dict(self):
        return {
            'side': self.side,
            'price': self.price,
            'quantity': self.quantity
        }


class OrderBook:
    def __init__(self):
        self.bids = {} #dictionary with key:price, value:[deque of Order objects]
        self.asks = {}
        #self.bids = {}  # dictionary with key: price, value: [list of Order objects]
        #self.asks = {}
        self.price = 0
        self.last_order = None

    def to_json(self):
        bids_data = {price: [order.to_dict() for order in orders] for price, orders in self.bids.items()}
        asks_data = {price: [order.to_dict() for order in orders] for price, orders in self.asks.items()}
        last_order = self.last_order.to_dict() if self.last_order else 'n/a'

        return {
            'price': self.price,
            'bids': bids_data,
            'asks': asks_data,
            'last_order' : last_order
        }
    
    def get_status(self):
        return self.to_json()
    
    def add_order_to_book(self, order):
        if order.side == 'buy':
            if order.price not in self.bids:
                self.bids[order.price] = deque()
            self.bids[order.price].append(order)
        elif order.side == 'sell':
            if order.price not in self.asks:
                self.asks[order.price] = deque()
            self.asks[order.price].append(order)
    

    def buy_order(self, order):
        if self.asks and order.price >= min(self.asks): # buy order is above or equal to lowest ask price
            self.execute_buy(order)
        else:
            self.add_order_to_book(order)

    def sell_order(self, order):
        if self.bids and order.price <= max(self.bids): # sell order is below or equal to highest bid price
            self.execute_sell(order)
        else:
            self.add_order_to_book(order)

    def execute_buy(self, buyorder):
        print(f"executing buy at {buyorder.price} qty {buyorder.quantity}")
        while(buyorder.quantity > 0 and self.asks):
            if(min(self.asks) <= buyorder.price): # lowest ask is less or equal to the buy order price
                self.price = min(self.asks) # self.asks item is a dict with key price, value deque of Order objects
                print(f"self.price is {self.price}")
                sell_orders_at_price = self.asks[self.price] # reference deque of all sell orders at this price
                front_sell_order_at_price = sell_orders_at_price.popleft() # get the first/oldest sell order at this price(from front of deque)
                print(f"first sell order at price {front_sell_order_at_price.price} qty {front_sell_order_at_price.quantity}")
                if front_sell_order_at_price.quantity < buyorder.quantity:
                    # this sell order is not enough to fill the entire buy order, 
                    # we do nothing more to the sell order since it is already popped from the deque,
                    # we decrement buyorder quantity by the contracts of the sell order
                    print(f"that is not enough to fill the whole buy order")
                    buyorder.quantity -= front_sell_order_at_price.quantity
                    print(f"buyorder qty is now {buyorder.quantity}")
                    if not self.asks[self.price]:  # also remove the price entry from dict if its deque of orders is empty
                        del self.asks[self.price]
                        print(f"deleted self.asks entry at {self.price}")
                else: # current sell order is enough to fill the entire buy order
                    print(f"it is enough to fill the entire buy order")       
                    front_sell_order_at_price.quantity -= buyorder.quantity
                    buyorder.quantity = 0
                    print(f"remaining sell order qty {front_sell_order_at_price.quantity}")
                    if front_sell_order_at_price.quantity > 0: #this particular sell order still has contracts remaining unfilled, so add it back to the front of the deque of sell orders at its price
                        sell_orders_at_price.appendleft(front_sell_order_at_price)
                        print(f"appending remaing sell order back to the orders at this price.")
            else: #lowest ask is not less or equal to the buy price, so add the buy order to list of bids and return.
                self.add_order_to_book(buyorder)
                print(f"adding buy order to book, no asks sufficient to fill it.")
                break
        else: #lowest ask is not less or equal to the buy price, so add the buy order to list of bids and return.
                self.add_order_to_book(buyorder)
                print(f"adding buy order to book, no asks sufficient to fill it.")

    def execute_sell(self, sellorder):
        while(sellorder.quantity > 0 and self.bids):
            if(max(self.bids) >= sellorder.price): # highest bid is above or equal to the sell order price
                self.price = max(self.bids) # self.bids item is a dict with key price, value deque of Order objects
                buy_orders_at_price = self.bids[self.price] # reference deque of all buy orders at this price
                front_buy_order_at_price = buy_orders_at_price.popleft() # get the first/oldest buy order at this price
                if front_buy_order_at_price.quantity < sellorder.quantity:
                    # this buy order is not enough to fill the entire sell order, 
                    # we do nothing more to the buy order since it is already popped from the deque,
                    # we decrement sellorder quantity by the contracts of the buy order
                    sellorder.quantity -= front_buy_order_at_price.quantity
                    if not self.bids[self.price]:  # also remove the price entry from dict if its deque of orders is empty
                        del self.bids[self.price]
                else: # current buy order is enough to fill the entire sell order       
                    front_buy_order_at_price.quantity -= sellorder.quantity
                    sellorder.quantity == 0
                    if front_buy_order_at_price.quantity > 0: #this particular buy order still has contracts remaining unfilled, so add it back to the front of the deque of buy orders at its price
                        buy_orders_at_price.appendleft(front_buy_order_at_price)
            else: #highest bid is not above or equal to the sell price, so add the sell order to list of asks and return.
                self.add_order_to_book(sellorder)
                break
        else: #highest bid is not above or equal to the sell price, so add the sell order to list of asks and return.
                self.add_order_to_book(sellorder)
    
    # def add_order(self, order):
    #     self.last_order = order
    #     if order.side == 'buy':
    #         if order.price in self.bids:
    #             self.bids[order.price].append(order)
    #         else:
    #             self.bids[order.price] = [order]
    #     elif order.side == 'sell':
    #         if order.price in self.asks:
    #             self.asks[order.price].append(order)
    #         else:
    #             self.asks[order.price] = [order]
    #     self.match_orders()
    
    # def match_orders(self):
    #     for buy_price in sorted(self.bids.keys(), reverse=True):
    #         for sell_price in sorted(self.asks.keys()):
    #             if buy_price >= sell_price:
    #                 print(f"trying to match buy{buy_price} to sell{sell_price}")
    #                 matched_quantity = min(
    #                     sum(o.quantity for o in self.bids[buy_price]),
    #                     sum(o.quantity for o in self.asks[sell_price])
    #                 )
    #                 print(f" matched {matched_quantity}")
    #                 self.price = sell_price
    #                 self.execute_orders(self.bids[buy_price], matched_quantity)
    #                 self.execute_orders(self.asks[sell_price], matched_quantity)
    #                 print(self.get_status()) # this doesnt work 
    #                 if not self.bids[buy_price]:
    #                     print (f"removing bids key at {buy_price}")
    #                     del self.bids[buy_price]
    #                     if not self.asks[sell_price]:
    #                         print (f"also removing asks key at {sell_price}")
    #                         del self.asks[sell_price]
    #                     break
    #                 if not self.asks[sell_price]:
    #                     print (f"removing asks key at {sell_price}")
    #                     del self.asks[sell_price]
    #                     break
    
    # def execute_orders(self, orders, quantity):
    #     remaining_quantity = quantity
    #     while remaining_quantity > 0 and orders:
    #         order = orders.pop(0)
    #         if order.quantity <= remaining_quantity:
    #             remaining_quantity -= order.quantity
    #         else:
    #             order.quantity -= remaining_quantity
    #             remaining_quantity = 0
    #             orders.insert(0, order)


    def process_order_update(self, add_or_remove, order):
        self.last_order = order
        if add_or_remove == 'add':
            if(order.side == 'buy'):
                self.buy_order(order)
            elif (order.side == 'sell'):
                self.sell_order(order)
        return self


    
    

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