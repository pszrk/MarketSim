from flask import Flask, request, jsonify
from orderbook import order_book, Order

app = Flask(__name__)

#  endpoint to submit orders
@app.route("/submit/", methods =["POST"])
def receive_order():
    data = request.get_json()

    #  data validation
    if "price" not in data or not data["price"]:
        return jsonify({"error": "Missing price parameter"}), 400   
    if "qty" not in data or not data["qty"]:
        return jsonify({"error": "Missing qty parameter"}), 400
    if "side" not in data or data["side"] not in ["bid", "ask"]:
        return jsonify({"error": "Missing side parameter"}), 400    
    
    try:
        price = float(data["price"])
        qty = int(data["qty"])
        side = data["side"]

        if price <= 0:
            return jsonify({"error": "Price must be a positive number"}), 400   
        if qty <= 0:
            return jsonify({"error": "Quantity must be a positive number"}), 400    
        
        order = Order(side, price, qty)
        order_book.add_order(order)
        order_book.match_orders()

        return jsonify({"message": "Order received successfully"}), 200

    except ValueError:
        return jsonify({"error": "Invalid format for price or quantity"}), 400        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/orderbook/", methods =["GET"])
def get_orderbook():
    order_book_state = {
        "bids": order_book.bids,
        "asks": order_book.asks
    }
    return jsonify(order_book_state), 200
