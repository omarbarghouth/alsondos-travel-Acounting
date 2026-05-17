from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_all, get_by_id, insert, update, delete, search

suppliers_bp = Blueprint('suppliers', __name__)

FIELDS = [
    ('name',           'Supplier Name',          'text',     True,  []),
    ('type',           'Type',                   'select',   True,  ['Airline','Hotel','Tour Operator','Transfer','Visa Agent','Insurance','Other']),
    ('contact_name',   'Contact Person',         'text',     False, []),
    ('phone',          'Phone',                  'text',     False, []),
    ('email',          'Email',                  'email',    False, []),
    ('country',        'Country',                'text',     False, []),
    ('city',           'City',                   'text',     False, []),
    ('account_number', 'Account / IATA No.',     'text',     False, []),
    ('payment_terms',  'Payment Terms',          'text',     False, []),
    ('notes',          'Notes',                  'textarea', False, []),
]

@suppliers_bp.route('/')
def index():
    q = request.args.get('q', '')
    recs = search('suppliers', q, ['name','type','contact_name','city']) if q else get_all('suppliers')
    recs = sorted(recs, key=lambda x: x.get('created_at',''), reverse=True)
    return render_template('pages/suppliers/index.html', records=recs, q=q, fields=FIELDS, delete_fn='suppliers.delete_supplier')

@suppliers_bp.route('/new', methods=['GET','POST'])
def new():
    if request.method == 'POST':
        insert('suppliers', {f[0]: request.form.get(f[0],'') for f in FIELDS})
        flash('Supplier added.', 'success')
        return redirect(url_for('suppliers.index'))
    return render_template('pages/suppliers/form.html', record={}, fields=FIELDS, is_edit=False)

@suppliers_bp.route('/<id>/edit', methods=['GET','POST'])
def edit(id):
    rec = get_by_id('suppliers', id)
    if not rec:
        flash('Supplier not found.', 'danger')
        return redirect(url_for('suppliers.index'))
    if request.method == 'POST':
        update('suppliers', id, {f[0]: request.form.get(f[0],'') for f in FIELDS})
        flash('Supplier updated.', 'success')
        return redirect(url_for('suppliers.index'))
    return render_template('pages/suppliers/form.html', record=rec, fields=FIELDS, is_edit=True)

@suppliers_bp.route('/<id>/delete', methods=['POST'])
def delete_supplier(id):
    delete('suppliers', id)
    flash('Supplier deleted.', 'success')
    return redirect(url_for('suppliers.index'))
