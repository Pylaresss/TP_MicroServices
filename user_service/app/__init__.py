from flask import Flask
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

app.config["DATABASE"] = os.path.join(DATA_DIR, "app.db")

from app.db import init_db
with app.app_context():
    init_db()

from app import views  # noqa
