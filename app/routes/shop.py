from flask import Blueprint, render_template
from app.models import Product
from app import db

shop_bp = Blueprint("shop", __name__)

@shop_bp.route("/")
def shop_home():
    products = Product.query.all()
    return render_template("shop.html", products=products)
