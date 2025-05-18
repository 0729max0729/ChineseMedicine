from flask import Blueprint

bp = Blueprint('shop', __name__)

@bp.route('/')
def index():
    return 'Homepage'