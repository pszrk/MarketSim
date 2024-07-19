

class Order:
    def __init__(self, side, price, quantity):
        self.side = side
        self.price = price
        self.quantity = quantity

class OrderBook:
    def __init__(self):
        self.bids = {}  #empty dictionary
        self.asks = {}
        self.price = 0
        self.last_order = 'n/a'
        self.bid = 0
        self.ask = 0
        self.filled_from_book = []

    def add_order(self, order):
        if(order.side == 'bid'):
            if(order.price) in self.bids:
                self.bids[order.price] += order.quantity
            else:
                self.bids[order.price] = order.quantity
        if(order.side == 'ask'):
            if order.price in self.asks:
                self.asks[order.price] += order.quantity
            else:
                self.asks[order.price] = order.quantity
    
    def match_orders(self):
        while self.bids and self.asks:
            best_bid_price = max(self.bids)     #  highest key in self.bids dictionary
            best_ask_price = min(self.asks)     #  lowest key in self.asks dictionary
            
            if best_bid_price >= best_ask_price:    
                # Match orders
                best_bid_order_qty = self.bids[best_bid_price]     # key = best bid price; value = quantity associated with that key in the bids dictionary
                best_ask_order_qty = self.asks[best_ask_price]     # key = best ask price; value = quantity associated with that key in the asks dictionary
                
                matched_quantity = min(best_bid_order_qty, best_ask_order_qty)
                print(f"Matched {matched_quantity} @ {best_ask_price}")
                        
                self.bids[best_bid_price] -= matched_quantity    # adjust the value associated with best_bid_price key
                self.asks[best_ask_price] -= matched_quantity    # adjust the value associated with best_ask_price key
                        
                if self.bids[best_bid_price] == 0:      #  the value associated with best_bid_price key is zero
                    del self.bids[best_bid_price]           #  delete best_bid_price key from dictionary              
                if self.asks[best_ask_price] == 0:      #  the value associated with best_ask_price key is zero
                    del self.asks[best_ask_price]           #  delete best_ask_price key from dictionary

            else:  #  best bid price is not above or equal best ask price
                break

    def display_orderbook(self):
        print("BIDS:")
        for key, value in self.bids.items():
            print(f"BID Price: {key}, Qty: {value}")
        
        print("\nASKS:")
        for key, value in self.asks.items():
            print(f"ASK Price: {key}, Qty: {value}")


if __name__ == "__main__":
    order_book = OrderBook()

    order_book.add_order(Order('bid', 100, 10))
    order_book.add_order(Order('bid', 99, 5))
    order_book.add_order(Order('bid', 98, 8))

    order_book.add_order(Order('ask', 99, 25))
    order_book.add_order(Order('ask', 103, 7))

    print("Initial Orderbook State:")
    order_book.display_orderbook()

    order_book.match_orders()

    print("\nUpdated Orderbook State:")
    order_book.display_orderbook()