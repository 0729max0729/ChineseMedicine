from flask import Blueprint, render_template
shop_bp = Blueprint("shop", __name__)

@shop_bp.route("/")
def shop_index():
    return render_template("templates/shop.html")
