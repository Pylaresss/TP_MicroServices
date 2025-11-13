from flask import Flask

app = Flask(__name__)
app.config["JWT_SECRET"] = "change-me"  # même clé que la gateway

from app import views  # noqa
