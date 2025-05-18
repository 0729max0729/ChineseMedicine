from flask import Blueprint

bp = Blueprint('user', __name__)

@bp.route('/profile')
def profile():
    return 'User Profile'