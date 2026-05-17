"""
app.py — Alsondos Travel & Tourism ERP System
Entry point. Registers all blueprints and template filters.
"""
from flask import Flask, redirect, url_for

from routes.dashboard    import dashboard_bp
from routes.transactions import transactions_bp
from routes.suppliers    import suppliers_bp
from routes.companies    import companies_bp
from routes.customers    import customers_bp
from routes.hotels       import hotels_bp
from routes.tours        import tours_bp
from routes.transfers    import transfers_bp
from routes.payments     import payments_bp
from routes.statements   import statements_bp
from routes.vouchers     import vouchers_bp
from routes.invoices     import invoices_bp
from routes.settings     import settings_bp

app = Flask(__name__)
app.secret_key = 'alsondos-erp-secret-key-2024-change-in-production'

# ── Register blueprints ──────────────────────────────────────
app.register_blueprint(dashboard_bp)
app.register_blueprint(transactions_bp, url_prefix='/transactions')
app.register_blueprint(suppliers_bp,    url_prefix='/suppliers')
app.register_blueprint(companies_bp,    url_prefix='/companies')
app.register_blueprint(customers_bp,    url_prefix='/customers')
app.register_blueprint(hotels_bp,       url_prefix='/hotels')
app.register_blueprint(tours_bp,        url_prefix='/tours')
app.register_blueprint(transfers_bp,    url_prefix='/transfers')
app.register_blueprint(payments_bp,     url_prefix='/payments')
app.register_blueprint(statements_bp,   url_prefix='/statements')
app.register_blueprint(vouchers_bp,     url_prefix='/vouchers')
app.register_blueprint(invoices_bp,     url_prefix='/invoices')
app.register_blueprint(settings_bp,     url_prefix='/settings')

@app.route('/')
def root():
    return redirect(url_for('dashboard.index'))

# ── Template filters ─────────────────────────────────────────

@app.template_filter('jod')
def jod_filter(value):
    """Format number as JOD currency with 3 decimals."""
    try:
        return f"{float(value):,.3f} JOD"
    except (TypeError, ValueError):
        return "0.000 JOD"

@app.template_filter('dateformat')
def date_filter(value, fmt='%d %b %Y'):
    """Format ISO date string to readable format."""
    if not value:
        return '—'
    from datetime import datetime
    for f in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f'):
        try:
            return datetime.strptime(str(value)[:19], f[:len(str(value)[:19])]).strftime(fmt)
        except ValueError:
            continue
    return str(value)

@app.template_filter('stars')
def stars_filter(n):
    try:
        return '★' * int(n) + '☆' * (5 - int(n))
    except:
        return ''

if __name__ == '__main__':
    app.run(debug=True, port=5000)
