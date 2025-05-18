import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://hanmo_db_user:xb6Y6B7BaxplZaz4UP37QRkQUvmw2PRg@dpg-d0kom1t6ubrc73bfef5g-a/hanmo_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
