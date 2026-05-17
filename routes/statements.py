"""
statements.py — Unified account statement module.
- Single page with filters: company / customer / supplier / date / search.
- Statement dropdowns include entities from formal records AND from typed
  names in transactions (auto-discovery).
- Shows: sell_price (Amount) + per-row paid + remaining. NEVER net_cost or profit.
- Supplier ledger: outbound + return split.
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

    all_txns    = get_all('transactions')

    # ── Build enriched dropdown lists ─────────────────────────
    # Include formal records + any unique names found in transactions
    companies = _enrich_list(get_all('companies'), all_txns, 'company', 'sell_to', 'company_id')
    customers = _enrich_list(get_all('customers'), all_txns, 'customer', 'customer_name', 'customer_id')
    suppliers = _enrich_list(get_all('suppliers'), all_txns, 'supplier', 'supplier_name', 'supplier_id')

    entity      = None
    entity_type = None
    ledger      = []
    summary     = {}
    has_filter  = bool(company_id or customer_id or supplier_id)

    if supplier_id:
        entity = _find_entity(get_all('suppliers'), supplier_id, all_txns, 'supplier', 'supplier_name', 'supplier_id')
        if entity:
            entity_type = 'supplier'
            ledger, summary = _build_supplier_ledger(entity, supplier_id, date_from, date_to, q, all_txns)
    elif company_id:
        entity = _find_entity(get_all('companies'), company_id, all_txns, 'company', 'sell_to', 'company_id')
        if entity:
            entity_type = 'company'
            ledger, summary = _build_client_ledger(entity, 'company', company_id, date_from, date_to, q, all_txns)
    elif customer_id:
        entity = _find_entity(get_all('customers'), customer_id, all_txns, 'customer', 'customer_name', 'customer_id')
        if entity:
            entity_type = 'customer'
            ledger, summary = _build_client_ledger(entity, 'customer', customer_id, date_from, date_to, q, all_txns)

    return render_template(
        'pages/statements/index.html',
        companies=companies, customers=customers, suppliers=suppliers,
        company_id=company_id, customer_id=customer_id, supplier_id=supplier_id,
        date_from=date_from, date_to=date_to, q=q,
        entity=entity, entity_type=entity_type,
        ledger=ledger, summary=summary, has_filter=has_filter,
    )


# ── Ledger builders ──────────────────────────────────────────

def _build_client_ledger(entity, entity_type, entity_id, date_from, date_to, q, all_txns=None):
    """
    Per-transaction rows showing: Amount (sell_price), Paid, Remaining.
    Followed by standalone payment rows for partial payments.
    NEVER shows net_cost or profit.
    """
    if all_txns is None:
        all_txns = get_all('transactions')
    all_pays = get_all('payments')

    # Match transactions to this entity (by ID or by name)
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

    # Payments for these transactions
    all_related_pays = [p for p in all_pays if p.get('transaction_id') in txn_ids]

    rows = []
    total_invoiced = 0.0
    total_paid_all = 0.0

    for t in txns:
        sell_price = float(t.get('sell_price') or 0)
        # Payments for this specific transaction
        txn_pays = [p for p in all_related_pays if p.get('transaction_id') == t['id']]
        paid_amt  = sum(float(p.get('amount') or 0) for p in txn_pays)
        remaining = sell_price - paid_amt

        # Collect payment refs for display
        pay_refs = ', '.join(
            (p.get('method','') + (' ' + p['reference'] if p.get('reference') else ''))
            for p in txn_pays
        ) if txn_pays else ''

        rows.append({
            'date':        t.get('booking_date', ''),
            'ref':         t.get('ref_number', ''),
            'description': _desc(t),
            'amount':      sell_price,
            'paid':        paid_amt,
            'remaining':   round(remaining, 3),
            'pay_refs':    pay_refs,
            'type':        'invoice',
            'txn_id':      t['id'],
            'status':      t.get('status', ''),
        })
        total_invoiced += sell_price
        total_paid_all += paid_amt

    rows.sort(key=lambda x: (x.get('date') or '', x.get('ref') or ''))

    if q:
        rows = [r for r in rows if
                q in (r.get('description') or '').lower() or
                q in (r.get('ref') or '').lower()]

    total_remaining = total_invoiced - total_paid_all
    summary = {
        'total_invoiced': round(total_invoiced, 3),
        'total_paid':     round(total_paid_all, 3),
        'outstanding':    round(total_remaining, 3),
    }
    return rows, summary


def _build_supplier_ledger(entity, entity_id, date_from, date_to, q, all_txns=None):
    """Supplier ledger — net_cost per leg. Internal use only."""
    if all_txns is None:
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

        # Outbound leg
        if t.get('supplier_id') == entity_id or _nm(t.get('supplier_name'), entity.get('name')):
            cost = float(t.get('outbound_cost') or t.get('net_cost') or 0)
            suffix = ' [Outbound]' if has_return else ''
            rows.append({
                'date': t.get('booking_date', ''), 'ref': t.get('ref_number', ''),
                'description': _desc(t) + suffix,
                'amount': cost, 'paid': 0.0,
                'remaining': cost, 'pay_refs': '',
                'type': 'purchase', 'txn_id': t['id'], 'status': t.get('status', ''),
            })

        # Return leg
        if has_return and (t.get('return_supplier_id') == entity_id or
                           _nm(t.get('return_supplier_name'), entity.get('name'))):
            ret_cost = float(t.get('return_cost') or 0)
            if ret_cost:
                rows.append({
                    'date': t.get('booking_date', ''), 'ref': t.get('ref_number', ''),
                    'description': _desc(t) + ' [Return]',
                    'amount': ret_cost, 'paid': 0.0,
                    'remaining': ret_cost, 'pay_refs': '',
                    'type': 'purchase', 'txn_id': t['id'], 'status': t.get('status', ''),
                })

    rows.sort(key=lambda x: (x.get('date') or '', x.get('ref') or ''))
    if q:
        rows = [r for r in rows if
                q in (r.get('description') or '').lower() or
                q in (r.get('ref') or '').lower()]

    total = sum(r['amount'] for r in rows)
    summary = {
        'total_invoiced': round(total, 3),
        'total_paid':     0.0,
        'outstanding':    round(total, 3),
    }
    return rows, summary


# ── Entity discovery helpers ─────────────────────────────────

def _enrich_list(formal_list, all_txns, entity_type, name_field, id_field):
    """
    Returns formal records + synthetic records for names that appear only
    in transactions (no formal record created yet).
    Synthetic records get a fake id = 'txn:' + name so the dropdown works.
    """
    known_names = {r['name'].strip().lower() for r in formal_list}
    known_ids   = {r['id'] for r in formal_list}

    extra = []
    seen_names = set()
    for t in all_txns:
        name = (t.get(name_field) or '').strip()
        if not name:
            continue
        # Also skip if the transaction is linked to a formal record
        if t.get(id_field) in known_ids:
            continue
        nl = name.lower()
        if nl not in known_names and nl not in seen_names:
            seen_names.add(nl)
            # Synthetic entry — id encodes the name so we can match it
            extra.append({
                'id':       'txn:' + name,
                'name':     name,
                '_synthetic': True,
            })

    return formal_list + sorted(extra, key=lambda x: x['name'])


def _find_entity(formal_list, entity_id, all_txns, entity_type, name_field, id_field):
    """Find entity by id — also handles synthetic 'txn:Name' ids."""
    # Formal record
    found = next((r for r in formal_list if r['id'] == entity_id), None)
    if found:
        return found
    # Synthetic
    if entity_id.startswith('txn:'):
        name = entity_id[4:]
        return {'id': entity_id, 'name': name, '_synthetic': True}
    return None


# ── Utilities ────────────────────────────────────────────────

def _nm(a, b):
    """Case-insensitive name match."""
    return bool(a and b and a.strip().lower() == b.strip().lower())


def _desc(t):
    parts = [t.get('service_type', 'Service')]
    if t.get('customer_name'):
        parts.append(t['customer_name'])
    if t.get('from_city') and t.get('to_city'):
        parts.append(f"{t['from_city']} → {t['to_city']}")
    elif t.get('hotel_name'):
        parts.append(t['hotel_name'])
    elif t.get('tour_name'):
        parts.append(t['tour_name'])
    parts.append(t.get('ref_number', ''))
    return '  ·  '.join(p for p in parts if p)
