from flask import request, jsonify
from app import app

ORDERS = []


@app.get("/")
def health():
    return jsonify({"status": "ok", "service": "orders_service"})


@app.post("/orders")
def create_order():
    data = request.json or {}
    username = data.get("username")
    article_id = data.get("article_id")
    prix = data.get("prix")

    if not username or not article_id or prix is None:
        return jsonify({"error": "missing fields"}), 400

    order = {
        "id": len(ORDERS) + 1,
        "username": username,
        "article_id": article_id,
        "prix": prix,
    }
    ORDERS.append(order)
    return jsonify(order), 201


@app.get("/orders")
def list_orders():
    username = request.args.get("username")
    if username:
        # 🔴 important : filtrer par username
        return jsonify([o for o in ORDERS if o["username"] == username])
    return jsonify(ORDERS)
