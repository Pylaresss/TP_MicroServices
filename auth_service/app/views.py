from flask import request, jsonify
from app import app
import datetime
import jwt
import requests


USER_SERVICE_URL = "http://127.0.0.1:5002"


def create_jwt(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    }
    token = jwt.encode(payload, app.config["JWT_SECRET"], algorithm="HS256")
    return token


@app.get("/")
def health():
    return jsonify({"status": "ok", "service": "auth_service"})


@app.post("/auth/login")
def login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "missing fields"}), 400

    # Vérification via user_service
    r = requests.post(f"{USER_SERVICE_URL}/users/check_credentials", json={
        "username": username,
        "password": password,
    })

    if r.status_code != 200:
        return jsonify({"error": "invalid credentials"}), 401

    token = create_jwt(username)
    return jsonify({"token": token}), 200


@app.post("/auth/verify")
def verify():
    data = request.json or {}
    token = data.get("token")
    if not token:
        return jsonify({"valid": False, "reason": "missing token"}), 400

    try:
        payload = jwt.decode(
            token,
            app.config["JWT_SECRET"],
            algorithms=["HS256"],
        )
        return jsonify({"valid": True, "payload": payload}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"valid": False, "reason": "expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"valid": False, "reason": "invalid"}), 401


# 🔥 NOUVEL ENDPOINT POUR RAFRAÎCHIR LE TOKEN
@app.post("/auth/refresh")
def refresh():
    data = request.json or {}
    old_token = data.get("token")

    if not old_token:
        return jsonify({"error": "missing token"}), 400

    try:
        # On décode l'ancien token (s'il est encore valide)
        payload = jwt.decode(
            old_token,
            app.config["JWT_SECRET"],
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        # Token déjà expiré → obligé de se reconnecter
        return jsonify({"error": "expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "invalid"}), 401

    username = payload.get("sub")
    if not username:
        return jsonify({"error": "invalid payload"}), 400

    # On génère un NOUVEAU token avec une nouvelle expiration
    new_token = create_jwt(username)

    return jsonify({
        "token": new_token,
        "message": "token refreshed",
    }), 200
