from app import app
from flask import render_template, request, redirect, url_for, session, abort, flash
import requests
from authlib.jose import jwt, JoseError


AUTH_SERVICE_URL = "http://127.0.0.1:5001"
ORDERS_SERVICE_URL = "http://127.0.0.1:5003"

# Catalogue d’articles affiché dans shop.html
ARTICLES = [
    {"id": "a1", "nom": "Clavier", "prix": 29.90},
    {"id": "a2", "nom": "Souris",  "prix": 19.90},
    {"id": "a3", "nom": "Écran",   "prix": 149.00},
]


def get_article(article_id):
    for a in ARTICLES:
        if a["id"] == article_id:
            return a
    return None


def get_current_user():
    token = session.get("token")
    if not token:
        return None
    try:
        claims = jwt.decode(
            token,
            app.config["JWT_SECRET"],
        )
        # Vérifie exp, etc.
        claims.validate()
        return claims.get("sub")
    except JoseError:
        return None


@app.route("/")
def index():
    # redirige vers login par défaut
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "GET":
        return render_template("login.html", error=error)

    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        error = "Veuillez remplir tous les champs."
        return render_template("login.html", error=error)

    # Appel à l'Auth Service pour obtenir le JWT
    try:
        r = requests.post(f"{AUTH_SERVICE_URL}/auth/login", json={
            "username": username,
            "password": password,
        })
    except requests.exceptions.RequestException:
        error = "Erreur de communication avec le service d'authentification."
        return render_template("login.html", error=error)

    if r.status_code != 200:
        error = "Identifiants invalides."
        return render_template("login.html", error=error)

    token = r.json()["token"]
    print("TOKEN RECU :", token)

    session["token"] = token
    flash("Connexion réussie.")
    return redirect(url_for("shop"))


@app.route("/shop")
def shop():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    token = session.get("token")   # On récupère le JWT

    return render_template(
        "shop.html",
        username=user,
        articles=ARTICLES,
        token=token           # On l'envoie au template (si tu veux l'afficher)
    )


@app.post("/acheter/<article_id>")
def acheter(article_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    article = get_article(article_id)
    if not article:
        abort(404)

    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    try:
        r = requests.post(
            f"{ORDERS_SERVICE_URL}/orders",
            json={
                "username": user,
                "article_id": article["id"],
                "prix": article["prix"],
            },
            headers=headers
        )
    except requests.exceptions.RequestException:
        flash("Erreur lors de la création de la commande.")
        return redirect(url_for("shop"))

    if r.status_code >= 400:
        flash("Erreur lors de la création de la commande.")
        return redirect(url_for("shop"))

    return redirect(url_for("merci", article_id=article_id))


@app.route("/merci/<article_id>")
def merci(article_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    article = get_article(article_id)
    if not article:
        abort(404)

    return render_template("merci.html", username=user, article=article)


@app.route("/history")
def history():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    try:
        r = requests.get(
            f"{ORDERS_SERVICE_URL}/orders",
            params={"username": user}
        )
        orders = r.json() if r.status_code == 200 else []
    except requests.exceptions.RequestException:
        orders = []

    articles_by_id = {a["id"]: a for a in ARTICLES}

    return render_template(
        "history.html",
        username=user,
        orders=orders,
        articles_by_id=articles_by_id
    )
