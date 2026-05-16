from flask import Flask
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.transactions import transactions_bp
from routes.payments import payments_bp
from routes.statements import statements_bp
from routes.vouchers import vouchers_bp
from routes.invoices import invoices_bp
from routes.contracts import contracts_bp
from routes.delivery import delivery_bp
from routes.audit import audit_bp

app = Flask(__name__)
app.secret_key = 'alsondos-erp-secret-key-2024'

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(statements_bp)
app.register_blueprint(vouchers_bp)
app.register_blueprint(invoices_bp)
app.register_blueprint(contracts_bp)
app.register_blueprint(delivery_bp)
app.register_blueprint(audit_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
