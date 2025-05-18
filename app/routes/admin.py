from flask import Blueprint

bp = Blueprint('admin', __name__)

@bp.route('/admin')
def admin_panel():
    return 'Admin Dashboard'