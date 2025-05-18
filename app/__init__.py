from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes.public import public_bp
    from app.routes.shop import shop_bp
    from app.routes.user import auth_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(shop_bp, url_prefix="/shop")
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app
