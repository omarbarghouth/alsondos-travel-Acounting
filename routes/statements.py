from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_all, get_by_id

statements_bp = Blueprint('statements', __name__)

@statements_bp.route('/')
def index():
    return render_template('pages/statements/index.html',
                           companies=get_all('companies'),
                           customers=get_all('customers'),
                           suppliers=get_all('suppliers'))

@statements_bp.route('/company/<id>')
def company_statement(id):
    entity = get_by_id('companies', id)
    if not entity:
        flash('Company not found.', 'danger')
        return redirect(url_for('statements.index'))
    return _render_statement(entity, 'company', id)

@statements_bp.route('/customer/<id>')
def customer_statement(id):
    entity = get_by_id('customers', id)
    if not entity:
        flash('Customer not found.', 'danger')
        return redirect(url_for('statements.index'))
    return _render_statement(entity, 'customer', id)

@statements_bp.route('/supplier/<id>')
def supplier_statement(id):
    entity = get_by_id('suppliers', id)
    if not entity:
        flash('Supplier not found.', 'danger')
        return redirect(url_for('statements.index'))

    date_from = request.args.get('from', '')
    date_to   = request.args.get('to', '')
    txns      = get_all('transactions')

    # Supplier sees net_cost (what we owe them), not sell_price
    txns = [t for t in txns if
            t.get('supplier_id') == id or
            (t.get('supplier_name','').lower() == entity.get('name','').lower())]
    if date_from: txns = [t for t in txns if (t.get('booking_date','') or '') >= date_from]
    if date_to:   txns = [t for t in txns if (t.get('booking_date','') or '') <= date_to]

    ledger  = []
    for t in txns:
        ledger.append({'date': t.get('booking_date',''), 'ref': t.get('ref_number',''),
                       'description': _desc(t), 'debit': float(t.get('net_cost') or 0), 'credit': 0, 'type':'purchase'})
    ledger.sort(key=lambda x: x.get('date',''))
    balance = 0
    for row in ledger:
        balance += row['debit'] - row['credit']
        row['balance'] = balance

    total_purchases = sum(r['debit'] for r in ledger)
    return render_template('pages/statements/supplier.html',
                           entity=entity, ledger=ledger,
                           total_purchases=total_purchases,
                           date_from=date_from, date_to=date_to)

def _render_statement(entity, entity_type, id):
    date_from = request.args.get('from', '')
    date_to   = request.args.get('to', '')
    all_txns  = get_all('transactions')
    all_pays  = get_all('payments')

    if entity_type == 'company':
        txns = [t for t in all_txns if t.get('company_id') == id or
                (t.get('sell_to','').lower() == entity.get('name','').lower())]
    else:
        txns = [t for t in all_txns if t.get('customer_id') == id or
                (t.get('customer_name','').lower() == entity.get('name','').lower())]

    if date_from: txns = [t for t in txns if (t.get('booking_date','') or '') >= date_from]
    if date_to:   txns = [t for t in txns if (t.get('booking_date','') or '') <= date_to]

    txn_ids = {t['id'] for t in txns}
    pays    = [p for p in all_pays if p.get('transaction_id') in txn_ids]

    # Build ledger — NEVER show net_cost or profit to clients
    ledger = []
    for t in txns:
        ledger.append({'date': t.get('booking_date',''), 'ref': t.get('ref_number',''),
                       'description': _desc(t), 'debit': float(t.get('sell_price') or 0),
                       'credit': 0, 'type':'invoice'})
    for p in pays:
        ledger.append({'date': p.get('payment_date',''), 'ref': p.get('ref_number',''),
                       'description': f"Payment — {p.get('method','')} {('Ref: '+p['reference']) if p.get('reference') else ''}".strip(),
                       'debit': 0, 'credit': float(p.get('amount') or 0), 'type':'payment'})

    ledger.sort(key=lambda x: x.get('date',''))
    balance = 0
    for row in ledger:
        balance += row['debit'] - row['credit']
        row['balance'] = balance

    total_invoiced = sum(r['debit']  for r in ledger)
    total_paid     = sum(r['credit'] for r in ledger)
    outstanding    = total_invoiced - total_paid
    return render_template('pages/statements/statement.html',
                           entity=entity, entity_type=entity_type,
                           ledger=ledger,
                           total_invoiced=total_invoiced,
                           total_paid=total_paid,
                           outstanding=outstanding,
                           date_from=date_from, date_to=date_to)

def _desc(t):
    parts = [t.get('service_type','Service'), t.get('customer_name','')]
    if t.get('from_city') and t.get('to_city'):
        parts.append(f"{t['from_city']} → {t['to_city']}")
    parts.append(t.get('ref_number',''))
    return ' — '.join(p for p in parts if p)
