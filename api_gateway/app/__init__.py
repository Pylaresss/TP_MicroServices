from flask import Flask
import os

app = Flask(__name__)

# Clé pour les sessions (stockage du JWT côté client)
app.secret_key = "gateway-secret"
app.config["JWT_SECRET"] = "change-me"  # même clé que auth_service

# Dossier data si tu veux encore l'utiliser plus tard
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

from app import views  # noqa
