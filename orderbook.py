from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
database_name = os.getenv("DB_NAME")
#print(f"DB_USERNAME: {username}, DB_HOST: {host}, DB_NAME: {database_name}")

engine = create_engine(f'mysql+mysqlconnector://{username}:{password}@{host}/{database_name}')
Base = declarative_base()

Session = sessionmaker(bind=engine)

class Order():
    def __init__(self, side, price, quantity):
        self.side = side
        self.price = price
        self.quantity = quantity
    

class Bid(Base):
    __tablename__ = 'bids'
    id = Column(Integer, primary_key=True)
    price = Column(Float)
    quantity = Column(Integer)

class Ask(Base):
    __tablename__ = 'asks'
    id = Column(Integer, primary_key=True)
    price = Column(Float)
    quantity = Column(Integer)

class Trade(Base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True)
    price = Column(Float)
    quantity = Column(Integer)
    time = Column(DateTime)

#  create tables in the database if they do not exist
Base.metadata.create_all(engine)

class OrderBook:
    def __init__(self):
        self.bids = {}  #  empty dictionary
        self.asks = {}
        self.newest_order = None

    def add_order(self, order):
        self.newest_order = order

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
                #print(f"Matched {matched_quantity} @ {best_ask_price}")

                #  record the trade in time&sales, filling limit orders using the newest order
                if self.newest_order:
                    trade_price = best_ask_price if self.newest_order.side == 'bid' else best_bid_price
                    self.record_trade(trade_price, matched_quantity, datetime.now())
                        
                self.bids[best_bid_price] -= matched_quantity    # adjust the value associated with best_bid_price key
                self.asks[best_ask_price] -= matched_quantity    # adjust the value associated with best_ask_price key
                        
                if self.bids[best_bid_price] == 0:      #  the value associated with best_bid_price key is zero
                    del self.bids[best_bid_price]           #  delete best_bid_price key from dictionary              
                if self.asks[best_ask_price] == 0:      #  the value associated with best_ask_price key is zero
                    del self.asks[best_ask_price]           #  delete best_ask_price key from dictionary

            else:  #  best bid price is not above or equal best ask price
                break

    def record_trade(self, price, qty, time):
        #  record a trade in time&sales table
        session = Session()
        try:
            new_trade = Trade(price=price, quantity=qty, time=time)
            session.add(new_trade)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Failed to record trade: {e}")
        finally:
            session.close()

    def get_trades(self):
        try:
            session = Session()
            trades = session.query(Trade).all()
            session.close()
            return trades
        except Exception as e:
            print(f"Failed to retrieve trades: {e}")
        finally:
            session.close()

    def display_orderbook(self):
        print("BIDS:")
        for key, value in self.bids.items():
            print(f"BID Price: {key}, Qty: {value}")        
        print("\nASKS:")
        for key, value in self.asks.items():
            print(f"ASK Price: {key}, Qty: {value}")

    def load_order_book_state(self):
        session = Session()
        try:
            #  populate bids from database
            bids = session.query(Bid).all()
            for bid in bids:
                self.bids[bid.price] = bid.quantity
            #  populate asks from database
            asks = session.query(Ask).all()
            for ask in asks:
                self.asks[ask.price] = ask.quantity

        except Exception as e:
            print(f"Failed to load order book state from database: {e}")
        finally:
            session.close()

    def save_order_book_state(self):
        session = Session()
        try:
            #  clear existing data in database
            session.query(Bid).delete()
            session.query(Ask).delete()

            #  insert new bids and asks
            for price, quantity in self.bids.items():
                new_bid = Bid(price=price, quantity=quantity)
                session.add(new_bid)
            for price, quantity in self.asks.items():
                new_ask = Ask(price=price, quantity=quantity)
                session.add(new_ask)

            session.commit()
            #print("saved orderbook state")
        except Exception as e:
            session.rollback()
            print(f"Failed to save order book state: {e}")
        finally:
            session.close()

    def get_orderbook_state(self):
        self.load_order_book_state()
        orderbook_state = {
            "bids": [],
            "asks": []
        }
        for price, quantity in self.bids.items():
            orderbook_state["bids"].append({"price": price, "quantity": quantity})
        for price, quantity in self.asks.items():
            orderbook_state["asks"].append({"price": price, "quantity": quantity})
        return orderbook_state


    def process_server_order(self, order):
        self.bids.clear()
        self.asks.clear()
        self.load_order_book_state()
        self.add_order(order)
        self.match_orders()
        self.save_order_book_state()


'''if __name__ == "__main__":
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
    order_book.display_orderbook()'''