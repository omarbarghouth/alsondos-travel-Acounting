"""
statements.py — Unified account statement module.
Single page with filters: company / customer / supplier / date / search.
NEVER exposes net_cost or profit to client statements.
"""
from flask import Blueprint, render_template, request
from database import get_all, get_by_id

statements_bp = Blueprint('statements', __name__)

@statements_bp.route('/')
def index():
    company_id  = request.args.get('company_id',  '')
    customer_id = request.args.get('customer_id', '')
    supplier_id = request.args.get('supplier_id', '')
    date_from   = request.args.get('date_from',   '')
    date_to     = request.args.get('date_to',     '')
    q           = request.args.get('q',           '').strip().lower()

    companies = get_all('companies')
    customers = get_all('customers')
    suppliers = get_all('suppliers')

    entity      = None
    entity_type = None
    ledger      = []
    summary     = {}
    has_filter  = bool(company_id or customer_id or supplier_id)

    if supplier_id:
        entity = get_by_id('suppliers', supplier_id)
        if entity:
            entity_type = 'supplier'
            ledger, summary = _build_supplier_ledger(entity, supplier_id, date_from, date_to, q)
    elif company_id:
        entity = get_by_id('companies', company_id)
        if entity:
            entity_type = 'company'
            ledger, summary = _build_client_ledger(entity, 'company', company_id, date_from, date_to, q)
    elif customer_id:
        entity = get_by_id('customers', customer_id)
        if entity:
            entity_type = 'customer'
            ledger, summary = _build_client_ledger(entity, 'customer', customer_id, date_from, date_to, q)

    return render_template(
        'pages/statements/index.html',
        companies=companies, customers=customers, suppliers=suppliers,
        company_id=company_id, customer_id=customer_id, supplier_id=supplier_id,
        date_from=date_from, date_to=date_to, q=q,
        entity=entity, entity_type=entity_type,
        ledger=ledger, summary=summary, has_filter=has_filter,
    )


def _build_client_ledger(entity, entity_type, entity_id, date_from, date_to, q):
    all_txns = get_all('transactions')
    all_pays = get_all('payments')

    if entity_type == 'company':
        txns = [t for t in all_txns if
                t.get('company_id') == entity_id or
                _nm(t.get('sell_to'), entity.get('name'))]
    else:
        txns = [t for t in all_txns if
                t.get('customer_id') == entity_id or
                _nm(t.get('customer_name'), entity.get('name'))]

    if date_from: txns = [t for t in txns if (t.get('booking_date') or '') >= date_from]
    if date_to:   txns = [t for t in txns if (t.get('booking_date') or '') <= date_to]

    txn_ids = {t['id'] for t in txns}
    pays = [p for p in all_pays if p.get('transaction_id') in txn_ids]
    if date_from: pays = [p for p in pays if (p.get('payment_date') or '') >= date_from]
    if date_to:   pays = [p for p in pays if (p.get('payment_date') or '') <= date_to]

    rows = []
    for t in txns:
        rows.append({
            'date': t.get('booking_date',''), 'ref': t.get('ref_number',''),
            'description': _desc(t), 'debit': float(t.get('sell_price') or 0),
            'credit': 0.0, 'type': 'invoice', 'txn_id': t['id'],
        })
    for p in pays:
        ref = p.get('reference','')
        rows.append({
            'date': p.get('payment_date',''), 'ref': p.get('ref_number',''),
            'description': 'Payment — ' + p.get('method','') + (f'  Ref: {ref}' if ref else ''),
            'debit': 0.0, 'credit': float(p.get('amount') or 0),
            'type': 'payment', 'txn_id': p.get('transaction_id',''),
        })

    rows.sort(key=lambda x: (x.get('date') or '', x.get('ref') or ''))
    if q:
        rows = [r for r in rows if q in (r.get('description')+''+r.get('ref','')).lower()]

    balance = 0.0
    for row in rows:
        balance += row['debit'] - row['credit']
        row['balance'] = round(balance, 3)

    total_invoiced = sum(r['debit']  for r in rows)
    total_paid     = sum(r['credit'] for r in rows)
    return rows, {
        'total_invoiced': round(total_invoiced, 3),
        'total_paid':     round(total_paid, 3),
        'outstanding':    round(total_invoiced - total_paid, 3),
    }


def _build_supplier_ledger(entity, entity_id, date_from, date_to, q):
    all_txns = get_all('transactions')
    txns = [t for t in all_txns if
            t.get('supplier_id') == entity_id or
            _nm(t.get('supplier_name'), entity.get('name')) or
            _nm(t.get('return_supplier_name'), entity.get('name')) or
            t.get('return_supplier_id') == entity_id]

    if date_from: txns = [t for t in txns if (t.get('booking_date') or '') >= date_from]
    if date_to:   txns = [t for t in txns if (t.get('booking_date') or '') <= date_to]

    rows = []
    for t in txns:
        has_return = bool(t.get('return_supplier_name') or t.get('return_supplier_id'))
        # Outbound supplier match
        if t.get('supplier_id') == entity_id or _nm(t.get('supplier_name'), entity.get('name')):
            cost = float(t.get('outbound_cost') or t.get('net_cost') or 0)
            lbl  = ' [Outbound]' if has_return else ''
            rows.append({'date': t.get('booking_date',''), 'ref': t.get('ref_number',''),
                         'description': _desc(t) + lbl,
                         'debit': cost, 'credit': 0.0, 'type': 'purchase', 'txn_id': t['id']})
        # Return supplier match
        if has_return and (t.get('return_supplier_id') == entity_id or
                           _nm(t.get('return_supplier_name'), entity.get('name'))):
            return_cost = float(t.get('return_cost') or 0)
            if return_cost:
                rows.append({'date': t.get('booking_date',''), 'ref': t.get('ref_number',''),
                             'description': _desc(t) + ' [Return]',
                             'debit': return_cost, 'credit': 0.0, 'type': 'purchase', 'txn_id': t['id']})

    rows.sort(key=lambda x: (x.get('date') or '', x.get('ref') or ''))
    if q:
        rows = [r for r in rows if q in (r.get('description')+''+r.get('ref','')).lower()]

    balance = 0.0
    for row in rows:
        balance += row['debit'] - row['credit']
        row['balance'] = round(balance, 3)

    total = sum(r['debit'] for r in rows)
    return rows, {'total_invoiced': round(total,3), 'total_paid': 0.0, 'outstanding': round(total,3)}


def _nm(a, b):
    return bool(a and b and a.strip().lower() == b.strip().lower())

def _desc(t):
    parts = [t.get('service_type','Service')]
    if t.get('customer_name'): parts.append(t['customer_name'])
    if t.get('from_city') and t.get('to_city'):
        parts.append(f"{t['from_city']} → {t['to_city']}")
    elif t.get('hotel_name'): parts.append(t['hotel_name'])
    parts.append(t.get('ref_number',''))
    return '  ·  '.join(p for p in parts if p)
