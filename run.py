from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User, Product
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash

import os
from werkzeug.utils import secure_filename



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
app = Flask(__name__)
app.config.from_object('config.Config')
app.secret_key = os.environ.get('SECRET_KEY')

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)

@app.route('/')
def index():
    products = Product.query.limit(5).all()
    return render_template('index.html', products=products)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/products')
def products():
    q = request.args.get('q', '').strip()
    query = Product.query
    if q:
        # 支援商品名稱、分類、描述模糊查詢
        search = f"%{q}%"
        query = query.filter(
            db.or_(
                Product.name.ilike(search),
                Product.description.ilike(search),
                Product.category.ilike(search)
            )
        )
    all_products = query.order_by(Product.id.desc()).all()

    categories = [
        ('aroma', '香薰/香氛'),
        ('tea', '花草茶/果乾水'),
        ('soap', '手工皂'),
        ('bodycare', '身體保養'),
        ('herbal', '養生藥膳'),
        ('dessert', '甜點飲品'),
        ('gift', '精品小物')
    ]
    category_dict = {key: [] for key, _ in categories}
    for product in all_products:
        if product.category in category_dict:
            category_dict[product.category].append(product)
        else:
            category_dict.setdefault(product.category, []).append(product)
    return render_template('products.html', categories=categories, category_dict=category_dict, q=q)


# 商品子分類頁（以香薰/香氛為例）
@app.route('/aroma')
def aroma():
    aroma_products = Product.query.filter(Product.category=='aroma').all()
    return render_template('aroma.html', aroma_products=aroma_products)

@app.route('/tea')
def tea():
    tea_products = Product.query.filter(Product.category=='tea').all()
    return render_template('tea.html', tea_products=tea_products)

@app.route('/soap')
def soap():
    soap_products = Product.query.filter(Product.category=='soap').all()
    return render_template('soap.html', soap_products=soap_products)

@app.route('/bodycare')
def bodycare():
    bodycare_products = Product.query.filter(Product.category=='bodycare').all()
    return render_template('bodycare.html', bodycare_products=bodycare_products)

@app.route('/herbal')
def herbal():
    herbal_products = Product.query.filter(Product.category=='herbal').all()
    return render_template('herbal.html', herbal_products=herbal_products)

@app.route('/dessert')
def dessert():
    dessert_products = Product.query.filter(Product.category=='dessert').all()
    return render_template('dessert.html', dessert_products=dessert_products)

@app.route('/gift')
def gift():
    gift_products = Product.query.filter(Product.category=='gift').all()
    return render_template('gift.html', gift_products=gift_products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/update_cart/<product_id>', methods=['POST'])
def update_cart(product_id):
    if 'cart' in session:
        cart = session['cart']
        quantity = int(request.form.get('quantity', 1))
        if quantity > 0:
            cart[product_id]['quantity'] = quantity
            session['cart'] = cart
            flash('已更新數量', 'info')
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' in session:
        cart = session['cart']
        if product_id in cart:
            del cart[product_id]
            session['cart'] = cart
            flash('已刪除商品', 'info')
    return redirect(url_for('cart'))


@app.route('/blog')
def blog():
    articles = []  # 你可以在這裡查詢文章列表
    return render_template('blog.html', articles=articles)

@app.route('/article/<int:article_id>')
def article(article_id):
    article = {'title': '示範文章', 'content': '這是內容'}  # 可替換為資料庫查詢
    return render_template('article.html', article=article)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # 這裡可以加上表單處理邏輯（如寄送 email）
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/cart')
def cart():
    cart_items = []  # 這裡用 session 或資料庫管理
    return render_template('cart.html', cart_items=cart_items)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    search_results = Product.query.filter(Product.name.ilike(f'%{query}%')).all() if query else []
    return render_template('search.html', search_results=search_results)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('profile'))
        else:
            flash('帳號或密碼錯誤，請重新輸入。', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if not User.query.filter_by(username=username).first():
            # 密碼加密
            hashed_password = generate_password_hash(password)
            user = User(username=username, email=email, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/profile')
def profile():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/order_history')
def order_history():
    return "<h1>訂單紀錄 (未實作)</h1>"

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'cart' not in session or not session['cart']:
        flash('購物車是空的', 'warning')
        return redirect(url_for('cart'))

    if request.method == 'POST':
        # 處理訂單資料，可存到資料庫
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        cart = session.get('cart', {})
        user_id = session.get('user_id')

        # 這裡示範印出或存檔
        print(f"下單人:{name} 地址:{address} 電話:{phone} 訂單內容:{cart} 會員ID:{user_id}")

        # TODO: 實際專案應存到 Order, OrderItem 資料表，寄信給店主
        session['cart'] = {}  # 清空購物車
        flash('訂單已送出！感謝您的購買。', 'success')
        return redirect(url_for('index'))

    return render_template('checkout.html')


@app.route('/admin/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        category = request.form['category']
        image_url = request.form.get('image_url', '')

        file = request.files.get('image_file')
        # 預設先用網址
        final_image_url = image_url.strip()

        # 若有上傳檔案且格式允許
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # 若檔名重複，自動加數字
            basename, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(save_path):
                filename = f"{basename}_{counter}{ext}"
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                counter += 1
            file.save(save_path)
            final_image_url = f"/static/uploads/{filename}"

        if not name or not price or not category:
            flash('請輸入商品名稱、價格和分類', 'danger')
            return render_template('add_product.html')
        
        new_product = Product(
            name=name,
            description=description,
            price=price,
            image_url=final_image_url,
            category=category
        )
        db.session.add(new_product)
        db.session.commit()
        flash('商品已成功上架！', 'success')
        return redirect(url_for('add_product'))

    return render_template('add_product.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render 會自動提供 PORT 環境變數
    app.run(host='0.0.0.0', port=port)
