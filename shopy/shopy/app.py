"""
Shopy - Full-Stack E-Commerce Web Application
Tech Stack: Python, Flask, SQLAlchemy (MySQL/SQLite), HTML, CSS, JavaScript

Run locally:
    pip install -r requirements.txt
    python app.py

By default this uses SQLite (zero setup, file: shopy.db).
To use MySQL instead, set the SHOPY_DB_URI environment variable, e.g.:
    export SHOPY_DB_URI="mysql+pymysql://user:password@localhost/shopy_db"
"""

import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SHOPY_SECRET_KEY", "dev-secret-key-change-in-production")

db_uri = os.environ.get("SHOPY_DB_URI", "sqlite:///shopy.db")
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(300), default="/static/img/placeholder.png")


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    product = db.relationship("Product")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def login_required(view_func):
    from functools import wraps

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user():
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    query = request.args.get("q", "").strip()
    if query:
        products = Product.query.filter(Product.name.ilike(f"%{query}%")).all()
    else:
        products = Product.query.all()
    return render_template("index.html", products=products, user=current_user(), query=query)


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product.html", product=product, user=current_user())


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "danger")
            return redirect(url_for("register"))

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id
        flash("Account created successfully!", "success")
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            flash("Logged in successfully!", "success")
            return redirect(url_for("index"))

        flash("Invalid email or password.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/cart")
@login_required
def cart():
    user = current_user()
    items = CartItem.query.filter_by(user_id=user.id).all()
    total = sum(item.product.price * item.quantity for item in items)
    return render_template("cart.html", items=items, total=total, user=user)


@app.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    user = current_user()
    existing = CartItem.query.filter_by(user_id=user.id, product_id=product_id).first()
    if existing:
        existing.quantity += 1
    else:
        db.session.add(CartItem(user_id=user.id, product_id=product_id, quantity=1))
    db.session.commit()
    flash("Added to cart.", "success")
    return redirect(request.referrer or url_for("index"))


@app.route("/cart/remove/<int:item_id>", methods=["POST"])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id == current_user().id:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for("cart"))


@app.route("/cart/checkout", methods=["POST"])
@login_required
def checkout():
    user = current_user()
    CartItem.query.filter_by(user_id=user.id).delete()
    db.session.commit()
    flash("Order placed successfully! Thank you for shopping with Shopy.", "success")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Database seeding (for demo purposes)
# ---------------------------------------------------------------------------
def seed_products():
    if Product.query.count() > 0:
        return
    demo_products = [
        Product(name="Wireless Headphones", description="Noise-cancelling over-ear headphones.", price=59.99, stock=25),
        Product(name="Mechanical Keyboard", description="RGB backlit mechanical keyboard.", price=79.99, stock=15),
        Product(name="Smart Watch", description="Fitness tracking smart watch.", price=99.50, stock=10),
        Product(name="USB-C Hub", description="7-in-1 USB-C hub with HDMI.", price=29.99, stock=40),
        Product(name="Laptop Stand", description="Adjustable aluminum laptop stand.", price=24.99, stock=30),
        Product(name="Portable SSD 1TB", description="High-speed external SSD.", price=89.99, stock=20),
    ]
    db.session.bulk_save_objects(demo_products)
    db.session.commit()


with app.app_context():
    db.create_all()
    seed_products()


if __name__ == "__main__":
    app.run(debug=True)
