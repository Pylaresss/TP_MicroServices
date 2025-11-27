from flask import request, jsonify
from app import app
import time
import requests
from authlib.jose import jwt, JoseError
import os

USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://127.0.0.1:5002")

# 🧠 Stockage en mémoire des tokens valides (STATEFUL)
VALID_ACCESS_TOKENS = set()
VALID_REFRESH_TOKENS = set()


def create_access_token(username: str) -> str:
    """
    Génère un ACCESS TOKEN (courte durée) pour accéder aux ressources protégées.
    Et l'enregistre dans la liste des tokens valides (stateful).
    """
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": username,
        "type": "access",
        "exp": int(time.time()) + 900,  # 15 minutes
    }

    token_bytes = jwt.encode(
        header,
        payload,
        app.config["JWT_SECRET"],
    )
    token = token_bytes.decode("utf-8")

    # On enregistre ce token comme valide côté serveur
    VALID_ACCESS_TOKENS.add(token)
    return token


def create_refresh_token(username: str) -> str:
    """
    Génère un REFRESH TOKEN (longue durée) pour obtenir de nouveaux access tokens.
    Lui aussi est enregistré côté serveur (stateful).
    """
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": username,
        "type": "refresh",
        "exp": int(time.time()) + 7 * 24 * 3600,  # 7 jours
    }

    token_bytes = jwt.encode(
        header,
        payload,
        app.config["JWT_SECRET"],
    )
    token = token_bytes.decode("utf-8")

    VALID_REFRESH_TOKENS.add(token)
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

    # Vérification via User Service
    r = requests.post(f"{USER_SERVICE_URL}/users/check_credentials", json={
        "username": username,
        "password": password,
    })

    if r.status_code != 200:
        return jsonify({"error": "invalid credentials"}), 401

    access_token = create_access_token(username)
    refresh_token = create_refresh_token(username)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
    }), 200


@app.post("/auth/verify")
def verify():
    """
    Vérifie un ACCESS TOKEN :
    - signature + exp via Authlib
    - présence dans VALID_ACCESS_TOKENS (stateful)
    """
    data = request.json or {}
    token = data.get("token")
    if not token:
        return jsonify({"valid": False, "reason": "missing token"}), 400

    # Vérifie d'abord s'il est encore dans la liste des tokens valides
    if token not in VALID_ACCESS_TOKENS:
        return jsonify({"valid": False, "reason": "revoked or unknown"}), 401

    try:
        claims = jwt.decode(token, app.config["JWT_SECRET"])
        claims.validate()

        if claims.get("type") != "access":
            return jsonify({"valid": False, "reason": "wrong token type"}), 401

        return jsonify({
            "valid": True,
            "payload": dict(claims),
        }), 200
    except JoseError as e:
        return jsonify({"valid": False, "reason": str(e)}), 401


@app.post("/auth/refresh")
def refresh():
    """
    Prend un REFRESH TOKEN valide, présent dans VALID_REFRESH_TOKENS,
    et renvoie un nouveau couple (access_token, refresh_token).
    """
    data = request.json or {}
    refresh_token = data.get("refresh_token")

    if not refresh_token:
        return jsonify({"error": "missing refresh_token"}), 400

    # Vérifie s'il est encore marqué comme valide côté serveur
    if refresh_token not in VALID_REFRESH_TOKENS:
        return jsonify({"error": "revoked or unknown refresh token"}), 401

    try:
        claims = jwt.decode(refresh_token, app.config["JWT_SECRET"])
        claims.validate()
    except JoseError as e:
        return jsonify({"error": str(e)}), 401

    if claims.get("type") != "refresh":
        return jsonify({"error": "wrong token type"}), 401

    username = claims.get("sub")
    if not username:
        return jsonify({"error": "invalid payload"}), 400

    # Rotation des refresh tokens : on invalide l'ancien
    VALID_REFRESH_TOKENS.discard(refresh_token)

    # On génère un nouveau couple de tokens
    new_access = create_access_token(username)
    new_refresh = create_refresh_token(username)

    return jsonify({
        "access_token": new_access,
        "refresh_token": new_refresh,
        "message": "tokens refreshed",
    }), 200