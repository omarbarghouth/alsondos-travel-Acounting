from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_all, get_by_id, insert, update, delete, next_number, search

payments_bp = Blueprint('payments', __name__)
METHODS = ['Cash', 'Bank Transfer', 'CliQ', 'Credit Card', 'Cheque']

@payments_bp.route('/')
def index():
    pays   = get_all('payments')
    q      = request.args.get('q', '')
    method = request.args.get('method', '')
    date_f = request.args.get('date_from', '')
    date_t = request.args.get('date_to', '')

    if q:
        pays = [p for p in pays if
                q.lower() in (p.get('ref_number','')  or '').lower() or
                q.lower() in (p.get('payer_name','')  or '').lower()]
    if method: pays = [p for p in pays if p.get('method') == method]
    if date_f: pays = [p for p in pays if (p.get('payment_date','') or '') >= date_f]
    if date_t: pays = [p for p in pays if (p.get('payment_date','') or '') <= date_t]

    pays = sorted(pays, key=lambda x: x.get('created_at',''), reverse=True)
    total_received = sum(float(p.get('amount') or 0) for p in pays)
    return render_template('pages/payments/index.html',
                           payments=pays, payment_methods=METHODS,
                           total_received=total_received,
                           q=q, method=method, date_f=date_f, date_t=date_t)

@payments_bp.route('/new', methods=['GET','POST'])
def new():
    txn_id = request.args.get('transaction_id', '')
    txn    = get_by_id('transactions', txn_id) if txn_id else None
    existing   = [p for p in get_all('payments') if p.get('transaction_id') == txn_id] if txn else []
    total_paid = sum(float(p.get('amount') or 0) for p in existing)
    remaining  = float((txn or {}).get('sell_price') or 0) - total_paid

    if request.method == 'POST':
        data = {
            'ref_number':     next_number('payments', 'PAY'),
            'transaction_id': request.form.get('transaction_id',''),
            'payer_name':     request.form.get('payer_name',''),
            'payer_type':     request.form.get('payer_type',''),
            'amount':         _flt('amount'),
            'method':         request.form.get('method',''),
            'payment_date':   request.form.get('payment_date',''),
            'reference':      request.form.get('reference',''),
            'notes':          request.form.get('notes',''),
        }
        insert('payments', data)
        flash(f"Payment {data['ref_number']} recorded.", 'success')
        tid = data['transaction_id']
        return redirect(url_for('transactions.view', id=tid) if tid else url_for('payments.index'))

    return render_template('pages/payments/form.html',
                           payment={}, transactions=get_all('transactions'),
                           payment_methods=METHODS,
                           txn=txn, remaining=remaining, total_paid=total_paid, is_edit=False)

@payments_bp.route('/<id>/edit', methods=['GET','POST'])
def edit(id):
    pay = get_by_id('payments', id)
    if not pay:
        flash('Payment not found.', 'danger')
        return redirect(url_for('payments.index'))
    if request.method == 'POST':
        update('payments', id, {
            'payer_name':   request.form.get('payer_name',''),
            'amount':       _flt('amount'),
            'method':       request.form.get('method',''),
            'payment_date': request.form.get('payment_date',''),
            'reference':    request.form.get('reference',''),
            'notes':        request.form.get('notes',''),
        })
        flash('Payment updated.', 'success')
        return redirect(url_for('payments.index'))
    return render_template('pages/payments/form.html',
                           payment=pay, transactions=get_all('transactions'),
                           payment_methods=METHODS,
                           txn=None, remaining=0, total_paid=0, is_edit=True)

@payments_bp.route('/<id>/delete', methods=['POST'])
def delete_payment(id):
    delete('payments', id)
    flash('Payment deleted.', 'success')
    return redirect(url_for('payments.index'))

def _flt(key):
    try: return float(request.form.get(key) or 0)
    except: return 0.0
