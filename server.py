from flask import Flask, request, jsonify

app = Flask(__name__)

#  receives post request with price/qty/side values, validates request data, and calls process_order()
@app.route("/submit/", methods =["POST"])
def receive_order():
    data = request.get_json()

    if "price" not in data or data["price"] =="":
        return jsonify({"error": "Missing price parameter"}), 400   
    if "qty" not in data or data["qty"] =="":
        return jsonify({"error": "Missing quantity parameter"}), 400
    if "side" not in data or data["side"] not in ["bid", "ask"]:
        return jsonify({"error": "Missing side parameter"}), 400
    
    #  price and quantity data validation:
    try:
        price = float(data["price"])
    except ValueError:
        return jsonify({"error": "Invalid price format, must be a number"}), 400
    if price <= 0:
        return jsonify({"error": "Price must be a positive number"}), 400    
    try:
        qty = int(data["price"])
    except ValueError:
        return jsonify({"error": "Invalid quantity format, must be an integer"}), 400
    if qty <= 0:
        return jsonify({"error": "Quantity must be a positive number"}), 400
    

    price = data["price"]
    qty = data["qty"]
    side = data["side"]

    process_order(price, qty, side)

