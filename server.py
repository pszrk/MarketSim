from flask import Flask, request, jsonify, render_template
from orderbook import OrderBook, Order
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/orderbook/": {"origins": "*", "methods": ["GET"]},
    r"/submit/": {"origins": "*", "methods": ["POST"]},
})

book = OrderBook()

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
        book.process_server_order(order)

        return jsonify({"message": "Order received successfully"}), 200

    except ValueError:
        return jsonify({"error": "Invalid format for price or quantity"}), 400        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/orderbook/", methods =["GET"])
def get_orderbook():
    order_book_state = book.get_orderbook_state()
    return jsonify(order_book_state), 200


@app.route("/")
def index():
    return render_template('index.html')


#if __name__ == "__main__":
#    app.run(debug=True)
