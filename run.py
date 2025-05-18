from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User, Product
import os


app = Flask(__name__)
app.config.from_object('config.Config')
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')


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
    return render_template('products.html')

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
        # 登入邏輯
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('profile'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 註冊邏輯
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if not User.query.filter_by(username=username).first():
            user = User(username=username, email=email, password=password)
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

@app.route('/checkout')
def checkout():
    return "<h1>結帳頁面（尚未實作）</h1>"
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render 會自動提供 PORT 環境變數
    app.run(host='0.0.0.0', port=port)
