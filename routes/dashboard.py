from flask import Blueprint, render_template
from database import get_all
from datetime import date

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def index():
    txns      = get_all('transactions')
    payments  = get_all('payments')
    customers = get_all('customers')
    suppliers = get_all('suppliers')

    # ── Real computed stats — no mocked values ───────────────
    total_sales     = sum(float(t.get('sell_price') or 0) for t in txns)
    total_cost      = sum(float(t.get('net_cost')   or 0) for t in txns)
    total_profit    = total_sales - total_cost
    total_collected = sum(float(p.get('amount')     or 0) for p in payments)
    outstanding     = total_sales - total_collected

    today   = date.today().isoformat()
    upcoming = [t for t in txns
                if (t.get('departure_date') or '') >= today
                and t.get('status') not in ('Cancelled', 'Refunded')]
    pending  = [t for t in txns if t.get('status') == 'Pending']

    recent = sorted(txns, key=lambda x: x.get('created_at', ''), reverse=True)[:8]

    stats = dict(
        total_sales     = total_sales,
        total_profit    = total_profit,
        outstanding     = outstanding,
        total_collected = total_collected,
        upcoming_count  = len(upcoming),
        pending_count   = len(pending),
        txn_count       = len(txns),
        customer_count  = len(customers),
        supplier_count  = len(suppliers),
    )
    return render_template('pages/dashboard.html', stats=stats, recent_txns=recent)
