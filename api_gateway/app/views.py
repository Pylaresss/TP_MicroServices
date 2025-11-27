from app import app
from flask import render_template, request, redirect, url_for, session, abort, flash
import requests
from functools import wraps
import os


AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://127.0.0.1:5001")
ORDERS_SERVICE_URL = os.environ.get("ORDERS_SERVICE_URL", "http://127.0.0.1:5003")

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


def verify_access_token(access_token: str):
    """
    Demande à Auth Service si l'access token est encore valide (STATEFUL).
    Retourne le payload (claims) si valide, None sinon.
    """
    try:
        r = requests.post(
            f"{AUTH_SERVICE_URL}/auth/verify",
            json={"token": access_token},
            timeout=3,
        )
    except requests.exceptions.RequestException:
        return None

    if r.status_code != 200:
        return None

    data = r.json()
    if not data.get("valid"):
        return None

    return data.get("payload") or {}


def get_current_user():
    """
    Récupère l'utilisateur courant en interrogeant Auth Service.
    Si l'access token est invalide/expiré, tente de le rafraîchir avec le refresh token.
    """
    access_token = session.get("access_token")
    refresh_token = session.get("refresh_token")

    if not access_token:
        return None

    # 1) On demande d'abord à Auth Service de vérifier l'access token
    claims = verify_access_token(access_token)
    if claims is not None:
        return claims.get("sub")

    # 2) Access token invalide → on tente un refresh si on a un refresh token
    if not refresh_token:
        return None

    try:
        r = requests.post(
            f"{AUTH_SERVICE_URL}/auth/refresh",
            json={"refresh_token": refresh_token},
            timeout=3,
        )
    except requests.exceptions.RequestException:
        return None

    if r.status_code != 200:
        return None

    data = r.json()
    new_access = data.get("access_token")
    new_refresh = data.get("refresh_token")

    if not new_access or not new_refresh:
        return None

    # On met à jour la session avec les nouveaux tokens
    session["access_token"] = new_access
    session["refresh_token"] = new_refresh

    # On redemande à /auth/verify pour récupérer les claims
    claims = verify_access_token(new_access)
    if claims is None:
        return None

    return claims.get("sub")


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect(url_for("login"))
        return f(user=user, *args, **kwargs)
    return wrapper


@app.route("/")
def index():
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

    # Appel Auth Service → obtenir access + refresh tokens
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

    data = r.json()
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")

    if not access_token or not refresh_token:
        error = "Réponse d'authentification invalide."
        return render_template("login.html", error=error)

    session["access_token"] = access_token
    session["refresh_token"] = refresh_token

    flash("Connexion réussie.")
    return redirect(url_for("shop"))


@app.route("/shop")
@login_required
def shop(user):
    access_token = session.get("access_token")

    return render_template(
        "shop.html",
        username=user,
        articles=ARTICLES,
        token=access_token,  # si tu veux encore l'afficher
    )


@app.post("/acheter/<article_id>")
@login_required
def acheter(user, article_id):
    article = get_article(article_id)
    if not article:
        abort(404)

    access_token = session.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}

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
@login_required
def merci(user, article_id):
    article = get_article(article_id)
    if not article:
        abort(404)

    return render_template("merci.html", username=user, article=article)


@app.route("/history")
@login_required
def history(user):
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