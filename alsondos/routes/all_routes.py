from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from mock_data import TRANSACTIONS, COMPANIES, SUPPLIERS, PAYMENTS, HOTELS, AUDIT_LOG

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

# ── TRANSACTIONS ──────────────────────────────────────────────
transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/transactions')
@login_required
def index():
    status_filter = request.args.get('status', '')
    company_filter = request.args.get('company', '')
    txns = TRANSACTIONS
    if status_filter:
        txns = [t for t in txns if t['status'] == status_filter]
    if company_filter:
        txns = [t for t in txns if t['company'] == company_filter]
    return render_template('pages/transactions.html', transactions=txns,
                           companies=COMPANIES, suppliers=SUPPLIERS,
                           status_filter=status_filter, company_filter=company_filter)

@transactions_bp.route('/transactions/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        flash('Transaction created successfully!', 'success')
        return redirect(url_for('transactions.index'))
    return render_template('pages/transaction_form.html', transaction=None,
                           companies=COMPANIES, suppliers=SUPPLIERS, title='New Transaction')

@transactions_bp.route('/transactions/<int:tid>/edit', methods=['GET', 'POST'])
@login_required
def edit(tid):
    txn = next((t for t in TRANSACTIONS if t['id'] == tid), None)
    if request.method == 'POST':
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('transactions.index'))
    return render_template('pages/transaction_form.html', transaction=txn,
                           companies=COMPANIES, suppliers=SUPPLIERS, title='Edit Transaction')

@transactions_bp.route('/transactions/<int:tid>')
@login_required
def view(tid):
    txn = next((t for t in TRANSACTIONS if t['id'] == tid), None)
    return render_template('pages/transaction_view.html', transaction=txn)

# ── PAYMENTS ──────────────────────────────────────────────────
payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/payments')
@login_required
def index():
    company_filter = request.args.get('company', '')
    pmts = PAYMENTS
    if company_filter:
        pmts = [p for p in pmts if p['company'] == company_filter]
    return render_template('pages/payments.html', payments=pmts, companies=COMPANIES,
                           company_filter=company_filter)

@payments_bp.route('/payments/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        flash('Payment recorded successfully!', 'success')
        return redirect(url_for('payments.index'))
    return render_template('pages/payment_form.html', companies=COMPANIES)

# ── STATEMENTS ────────────────────────────────────────────────
statements_bp = Blueprint('statements', __name__)

@statements_bp.route('/statements')
@login_required
def index():
    return render_template('pages/statements.html', companies=COMPANIES)

@statements_bp.route('/statements/<int:cid>')
@login_required
def company_statement(cid):
    company = next((c for c in COMPANIES if c['id'] == cid), None)
    company_txns = [t for t in TRANSACTIONS if t['company'] == company['name']]
    company_pmts = [p for p in PAYMENTS if p['company'] == company['name']]
    date_from = request.args.get('from', '')
    date_to = request.args.get('to', '')

    # Build ledger entries
    ledger = []
    balance = 0
    for t in company_txns:
        balance += t['sell_price']
        ledger.append({'date': t['departure'], 'description': f"Ticket — {t['customer']} ({t['from_city']} → {t['to_city']})",
                       'debit': t['sell_price'], 'credit': 0, 'balance': balance, 'type': 'transaction'})
    for p in company_pmts:
        balance -= p['amount']
        ledger.append({'date': p['date'], 'description': f"Payment — {p['method']}",
                       'debit': 0, 'credit': p['amount'], 'balance': balance, 'type': 'payment'})

    ledger.sort(key=lambda x: x['date'])
    # Recalculate running balance
    running = 0
    for entry in ledger:
        running += entry['debit'] - entry['credit']
        entry['balance'] = running

    total_debit = sum(e['debit'] for e in ledger)
    total_credit = sum(e['credit'] for e in ledger)
    final_balance = total_debit - total_credit

    return render_template('pages/statement_detail.html', company=company, ledger=ledger,
                           total_debit=total_debit, total_credit=total_credit,
                           final_balance=final_balance, date_from=date_from, date_to=date_to)

# ── VOUCHERS ──────────────────────────────────────────────────
vouchers_bp = Blueprint('vouchers', __name__)

@vouchers_bp.route('/vouchers')
@login_required
def index():
    return render_template('pages/vouchers.html', hotels=HOTELS, companies=COMPANIES)

@vouchers_bp.route('/vouchers/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        data = request.form.to_dict()
        return render_template('pages/voucher_print.html', data=data)
    return render_template('pages/voucher_form.html', hotels=HOTELS, companies=COMPANIES)

@vouchers_bp.route('/vouchers/<int:vid>/print')
@login_required
def print_voucher(vid):
    sample = {'hotel': 'Grand Hyatt Amman', 'guest': 'Ahmad Mansour', 'checkin': '2024-12-20',
              'checkout': '2024-12-25', 'rooms': '2', 'room_type': 'Deluxe', 'meal': 'BB',
              'company': 'Gulf Air Travel Co.', 'ref': f'VCH-{vid:04d}', 'nights': 5}
    return render_template('pages/voucher_print.html', data=sample)

# ── INVOICES ──────────────────────────────────────────────────
invoices_bp = Blueprint('invoices', __name__)

@invoices_bp.route('/invoices')
@login_required
def index():
    return render_template('pages/invoices.html', transactions=TRANSACTIONS, companies=COMPANIES)

@invoices_bp.route('/invoices/<int:tid>/print')
@login_required
def print_invoice(tid):
    txn = next((t for t in TRANSACTIONS if t['id'] == tid), TRANSACTIONS[0])
    return render_template('pages/invoice_print.html', txn=txn)

# ── CONTRACTS ─────────────────────────────────────────────────
contracts_bp = Blueprint('contracts', __name__)

@contracts_bp.route('/contracts')
@login_required
def index():
    return render_template('pages/contracts.html', companies=COMPANIES)

@contracts_bp.route('/contracts/new')
@login_required
def new():
    return render_template('pages/contract_form.html', companies=COMPANIES)

# ── DELIVERY ──────────────────────────────────────────────────
delivery_bp = Blueprint('delivery', __name__)

@delivery_bp.route('/delivery')
@login_required
def index():
    pending = [t for t in TRANSACTIONS if t['status'] in ('Pending', 'Confirmed')]
    done = [t for t in TRANSACTIONS if t['status'] == 'Delivered']
    return render_template('pages/delivery.html', pending=pending, done=done)

# ── AUDIT ─────────────────────────────────────────────────────
audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/audit')
@login_required
def index():
    return render_template('pages/audit.html', logs=AUDIT_LOG)
