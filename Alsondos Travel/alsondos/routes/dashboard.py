from flask import Blueprint, render_template, session, redirect, url_for
from mock_data import DASHBOARD_STATS, TRANSACTIONS, PAYMENTS, COMPANIES

dashboard_bp = Blueprint('dashboard', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@dashboard_bp.route('/dashboard')
@login_required
def index():
    role = session.get('role', 'admin')
    stats = DASHBOARD_STATS
    return render_template('pages/dashboard.html', stats=stats, role=role,
                           transactions=TRANSACTIONS, companies=COMPANIES)
