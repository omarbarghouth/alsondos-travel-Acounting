from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_all, get_by_id, insert, update, delete, next_number

invoices_bp = Blueprint('invoices', __name__)

STATUSES = ['Unpaid', 'Partial', 'Paid']

@invoices_bp.route('/')
def index():
    invs = sorted(get_all('invoices'), key=lambda x: x.get('created_at',''), reverse=True)
    return render_template('pages/invoices/index.html', invoices=invs)

@invoices_bp.route('/new', methods=['GET','POST'])
def new():
    if request.method == 'POST':
        data = _collect()
        data['invoice_number'] = next_number('invoices', 'INV')
        rec = insert('invoices', data)
        flash(f"Invoice {rec['invoice_number']} created.", 'success')
        return redirect(url_for('invoices.print_invoice', id=rec['id']))
    return render_template('pages/invoices/form.html',
                           invoice={}, is_edit=False, statuses=STATUSES,
                           companies=get_all('companies'),
                           customers=get_all('customers'),
                           txns=get_all('transactions'))

@invoices_bp.route('/<id>/edit', methods=['GET','POST'])
def edit(id):
    inv = get_by_id('invoices', id)
    if not inv:
        flash('Invoice not found.', 'danger')
        return redirect(url_for('invoices.index'))
    if request.method == 'POST':
        update('invoices', id, _collect())
        flash('Invoice updated.', 'success')
        return redirect(url_for('invoices.print_invoice', id=id))
    return render_template('pages/invoices/form.html',
                           invoice=inv, is_edit=True, statuses=STATUSES,
                           companies=get_all('companies'),
                           customers=get_all('customers'),
                           txns=get_all('transactions'))

@invoices_bp.route('/<id>/print')
def print_invoice(id):
    inv = get_by_id('invoices', id)
    if not inv:
        flash('Invoice not found.', 'danger')
        return redirect(url_for('invoices.index'))
    return render_template('pages/invoices/print.html', invoice=inv)

@invoices_bp.route('/<id>/delete', methods=['POST'])
def delete_invoice(id):
    delete('invoices', id)
    flash('Invoice deleted.', 'success')
    return redirect(url_for('invoices.index'))

def _collect():
    f   = request.form.get
    sub = _flt('subtotal')
    dis = _flt('discount')
    return {
        'transaction_id':  f('transaction_id',''),
        'bill_to_name':    f('bill_to_name',''),
        'bill_to_type':    f('bill_to_type','customer'),
        'bill_to_address': f('bill_to_address',''),
        'invoice_date':    f('invoice_date',''),
        'due_date':        f('due_date',''),
        'service_desc':    f('service_desc',''),
        'service_type':    f('service_type',''),
        'subtotal':        sub,
        'discount':        dis,
        'total':           round(sub - dis, 3),
        'payment_status':  f('payment_status','Unpaid'),
        'notes':           f('notes',''),
    }

def _flt(key):
    try: return float(request.form.get(key) or 0)
    except: return 0.0
