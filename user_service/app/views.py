from flask import request, jsonify
from app import app
from app.db import check_credentials, add_user


@app.get("/")
def health():
    return jsonify({"status": "ok", "service": "user_service"})


@app.post("/users/check_credentials")
def api_check_credentials():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "missing fields"}), 400

    ok = check_credentials(username, password)
    if not ok:
        return jsonify({"valid": False}), 401

    return jsonify({"valid": True}), 200


@app.post("/users")
def api_add_user():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "missing fields"}), 400

    add_user(username, password)
    return jsonify({"status": "created"}), 201
