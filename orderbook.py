from collections import deque
import copy

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
        self.price = 0
        self.last_order = 'n/a'
        self.bid = 0
        self.ask = 0
        self.filled_from_book = []

    def to_json(self):
        bids_data = {price: [order.to_dict() for order in orders] for price, orders in self.bids.items()}
        asks_data = {price: [order.to_dict() for order in orders] for price, orders in self.asks.items()}
        last_order = self.last_order
        recent_fills = [o.to_dict() for o in self.filled_from_book]
        return {
            'price': self.price,
            'bids': bids_data,
            'asks': asks_data,
            'last_order' : last_order,
            'bid': self.bid,
            'ask': self.ask,
            'recent_fills' : recent_fills
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


    def calculate_bid_ask(self):
        if len(self.bids) > 0:
            self.bid = max(self.bids)
        else:
            self.bid = 0
        if len(self.asks) > 0:
            self.ask = min(self.asks)
        else:
            self.ask = 0
    

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
                    self.filled_from_book.append(front_sell_order_at_price) # just add the sell order to current list of filled asks
                    # we decrement buyorder quantity by the contracts of the sell order
                    print(f"that is not enough to fill the whole buy order")
                    buyorder.quantity -= front_sell_order_at_price.quantity
                    print(f"buyorder qty is now {buyorder.quantity}")
                    if not self.asks[self.price]:  # also remove the price entry from dict if its deque of orders is empty
                        del self.asks[self.price]
                        print(f"deleted self.asks entry at {self.price}")
                else: # current sell order is enough to fill the entire buy order
                    print(f"it is enough to fill the entire buy order")    
                    if front_sell_order_at_price.quantity > buyorder.quantity:
                        #the sell order on the book got partially filled, and we want to add the order that got partially filled to list of fills for this incoming buy order. 
                        partialfill = copy.copy(front_sell_order_at_price)
                        partialfill.quantity = front_sell_order_at_price.quantity - buyorder.quantity
                        self.filled_from_book.append(partialfill)               
                    front_sell_order_at_price.quantity -= buyorder.quantity                    
                    buyorder.quantity = 0
                    # remove buy order bid price key from dict as well, if it was added earlier due to a partial fill.
                    if buyorder.price in self.bids and not self.bids[buyorder.price]:
                        del self.bids[buyorder.price]
                        print(f"removed buyorder bid key {buyorder.price} from dict")
                    print(f"remaining sell order qty {front_sell_order_at_price.quantity}")
                    if front_sell_order_at_price.quantity > 0: #this particular sell order still has contracts remaining unfilled, so add it back to the front of the deque of sell orders at its price
                        sell_orders_at_price.appendleft(front_sell_order_at_price)
                        print(f"appending remaing sell order back to the orders at this price.")
                    elif not self.asks[self.price]:
                        del self.asks[self.price]
                        print(f"sell order fully filled and no remaining asks at {self.price}, removing price from dict")
            else: #lowest ask is not less or equal to the buy price, so add the buy order to list of bids and return.
                self.add_order_to_book(buyorder)
                print(f"adding buy order to book, no asks sufficient to fill it.")
                return # return here to avoid double posting the order to the book
        if(buyorder.quantity > 0): #lowest ask is not less or equal to the buy price, so add the buy order to list of bids and return.
                self.add_order_to_book(buyorder)
                print(f"adding buy order to book, no asks sufficient to fill it.")
        

    def execute_sell(self, sellorder):
        print(f"executing sell at {sellorder.price} qty {sellorder.quantity}")
        while(sellorder.quantity > 0 and self.bids):
            if(max(self.bids) >= sellorder.price): # highest bid is above or equal to the sell order price
                self.price = max(self.bids) # self.bids item is a dict with key price, value deque of Order objects
                print(f"self.price is {self.price}")
                buy_orders_at_price = self.bids[self.price] # reference deque of all buy orders at this price
                front_buy_order_at_price = buy_orders_at_price.popleft() # get the first/oldest buy order at this price
                print(f"first buy order at price {front_buy_order_at_price.price} qty {front_buy_order_at_price.quantity}")
                if front_buy_order_at_price.quantity < sellorder.quantity:
                    # this buy order is not enough to fill the entire sell order, 
                    # we do nothing more to the buy order since it is already popped from the deque,
                    self.filled_from_book.append(front_buy_order_at_price) # just add the buy order to current list of filled bids
                    # we decrement sellorder quantity by the contracts of the buy order
                    print(f"that is not enough to fill the whole sell order")
                    sellorder.quantity -= front_buy_order_at_price.quantity
                    print(f"sellorder qty is now {sellorder.quantity}")
                    if not self.bids[self.price]:  # also remove the price entry from dict if its deque of orders is empty
                        del self.bids[self.price]
                        print(f"deleted self.bids entry at {self.price}")
                else: # current buy order is enough to fill the entire sell order
                    print(f"it is enough to fill the entire sell order")
                    if front_buy_order_at_price.quantity > sellorder.quantity:
                        # the sell order on the book got partially filled, and we want to add the order that got partially filled to list of fills for this incoming sell order. 
                        partialfill = copy.copy(front_buy_order_at_price)
                        partialfill.quantity = front_buy_order_at_price.quantity - sellorder.quantity
                        self.filled_from_book.append(partialfill)         
                    front_buy_order_at_price.quantity -= sellorder.quantity
                    sellorder.quantity = 0
                    # remove sell order ask price key from dict as well, if it was added earlier due to a partial fill.
                    if sellorder.price in self.asks and not self.asks[sellorder.price]:
                        del self.asks[sellorder.price]
                        print(f"removed sellorder ask key {sellorder.price} from dict")
                    print(f"remaining buy order qty {front_buy_order_at_price.quantity}")
                    if front_buy_order_at_price.quantity > 0: #this particular buy order still has contracts remaining unfilled, so add it back to the front of the deque of buy orders at its price
                        buy_orders_at_price.appendleft(front_buy_order_at_price)
                        print(f"appending remaing buy order back to the orders at this price.")
                    elif not self.bids[self.price]:
                        del self.bids[self.price]
                        print(f"buy order fully filled and no remaining bids at {self.price}, removing price from dict")
            else: #highest bid is not above or equal to the sell price, so add the sell order to list of asks and return.
                self.add_order_to_book(sellorder)
                print(f"adding sell order to book, no asks sufficient to fill it.")
                return # return here to avoid double posting the order to the book
        if(sellorder.quantity > 0): #highest bid is not above or equal to the sell price, so add the sell order to list of asks and return.
                self.add_order_to_book(sellorder)
                print(f"adding sell order to book, no asks sufficient to fill it.")
        


    def process_order_update(self, add_or_remove, order):
        self.filled_from_book.clear()
        self.last_order = f"{order.side} {order.quantity} @ {order.price}"
        if add_or_remove == 'add':
            if(order.side == 'buy'):
                self.buy_order(order)
            elif (order.side == 'sell'):
                self.sell_order(order)
        self.calculate_bid_ask()


if __name__ == "__main__":
    order_book = OrderBook()
    print("running orderbook.py as main")
    order_book.process_order_update('add', Order('buy', 46.45, 3))
    order_book.process_order_update('add', Order('buy', 48.45, 9))
    order_book.process_order_update('add', Order('sell', 45.71, 3))