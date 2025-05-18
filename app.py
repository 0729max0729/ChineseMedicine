from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from config import Config
from models import db, User, Product, Order
from forms import LoginForm, RegisterForm

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
    items = []
    total = 0
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        items.append({"product": product.name, "qty": qty})
        total += product.price * qty
    order = Order(user_email=current_user.email, items=str(items), total=total)
    db.session.add(order)
    db.session.commit()
    session['cart'] = {}

    msg = Message("翰墨藥香 訂單通知", recipients=[current_user.email])
    msg.body = f"感謝您的訂購！\n\n訂單內容：{items}\n總金額：{total} 元"
    mail.send(msg)

    flash("訂單完成，已寄出確認信")
    return redirect(url_for("shop"))

if __name__ == "__main__":
    app.run(debug=True)
