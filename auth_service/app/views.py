from flask import request, jsonify
from app import app
import time
from authlib.jose import jwt, JoseError
import requests


USER_SERVICE_URL = "http://127.0.0.1:5002"


def create_jwt(username: str) -> str:
    """
    Génère un JWT avec Authlib, valable 1 heure.
    """
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": username,
        "exp": int(time.time()) + 3600,  # expiration dans 1h (timestamp)
    }

    token_bytes = jwt.encode(header, payload, app.config["JWT_SECRET"])
    # Authlib renvoie des bytes -> on convertit en str
    return token_bytes.decode("utf-8")


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
        claims = jwt.decode(
            token,
            app.config["JWT_SECRET"],
        )
        # Vérifie exp, etc.
        claims.validate()
        # claims est un objet Claims -> on le cast en dict pour jsonify
        return jsonify({"valid": True, "payload": dict(claims)}), 200
    except JoseError as e:
        # Toute erreur (signature, expiration, format...)
        return jsonify({"valid": False, "reason": str(e)}), 401


@app.post("/auth/refresh")
def refresh():
    data = request.json or {}
    old_token = data.get("token")

    if not old_token:
        return jsonify({"error": "missing token"}), 400

    try:
        # On décode l'ancien token
        claims = jwt.decode(
            old_token,
            app.config["JWT_SECRET"],
        )
        # Si exp est dépassé, ça lèvera ici
        claims.validate()
    except JoseError as e:
        # Token déjà expiré ou invalide -> obligé de se reconnecter
        return jsonify({"error": str(e)}), 401

    username = claims.get("sub")
    if not username:
        return jsonify({"error": "invalid payload"}), 400

    # On génère un NOUVEAU token avec une nouvelle expiration
    new_token = create_jwt(username)

    return jsonify({
        "token": new_token,
        "message": "token refreshed",
    }), 200
