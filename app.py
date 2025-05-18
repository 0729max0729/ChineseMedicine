from flask import Flask, render_template, redirect, url_for, request, session, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
from config import Config
from models import db, User, Product, Order
from forms import LoginForm, RegisterForm
from ecpay_payment_sdk import ECPayPaymentSdk

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
mail = Mail(app)
login = LoginManager(app)
login.login_view = 'login'

admin = Admin(app)
with app.app_context():
    db.create_all()
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Product, db.session))
    admin.add_view(ModelView(Order, db.session))

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def shop():
    products = Product.query.all()
    return render_template("shop.html", products=products)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("註冊成功，請登入")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("shop"))
        flash("帳號或密碼錯誤")
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("shop"))

@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart
    flash("已加入購物車")
    return redirect(url_for("shop"))

@app.route("/cart")
def cart():
    cart = session.get('cart', {})
    items = []
    total = 0
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        items.append({"product": product, "qty": qty})
        total += product.price * qty
    return render_template("cart.html", items=items, total=total)

@app.route("/checkout")
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash("購物車為空")
        return redirect(url_for("shop"))

    items = []
    total = 0
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        items.append({"product": product.name, "qty": qty})
        total += product.price * qty

    order = Order(user_email=current_user.email, items=str(items), total=total, status="Pending")
    db.session.add(order)
    db.session.commit()

    ecpay = ECPayPaymentSdk(
        MerchantID='2000132',
        HashKey='5294y06JbISpM5x9',
        HashIV='v77hoKGq4kWxNNIS',
        Debug=True
    )

    trade_no = f"HM{order.id:06d}"
    form_params = {
        'MerchantTradeNo': trade_no,
        'MerchantTradeDate': order.created_at.strftime("%Y/%m/%d %H:%M:%S"),
        'TotalAmount': int(order.total),
        'TradeDesc': '翰墨藥香購物',
        'ItemName': "#".join([f"{i['product']} x{i['qty']}" for i in items]),
        'ReturnURL': request.url_root + 'ecpay_callback',
        'ClientBackURL': request.url_root,
        'ChoosePayment': 'ALL',
        'NeedExtraPaidInfo': 'Y'
    }

    html = ecpay.create_order(parameters=form_params)
    session['cart'] = {}
    return make_response(html)

@app.route("/ecpay_callback", methods=["POST"])
def ecpay_callback():
    data = request.form.to_dict()
    merchant_trade_no = data.get("MerchantTradeNo")
    rtn_code = data.get("RtnCode")
    if not merchant_trade_no or rtn_code != '1':
        return "ERROR"

    order_id = int(merchant_trade_no.replace("HM", ""))
    order = Order.query.get(order_id)
    if order:
        order.status = "Paid"
        db.session.commit()
        print(f"訂單 {order.id} 已付款")
    return "1|OK"

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@app.route("/orders")
@login_required
def orders():
    user_orders = Order.query.filter_by(user_email=current_user.email).order_by(Order.created_at.desc()).all()
    return render_template("orders.html", orders=user_orders)

if __name__ == "__main__":
    app.run(debug=True)
