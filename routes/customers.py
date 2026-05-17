from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_all, get_by_id, insert, update, delete, search

customers_bp = Blueprint('customers', __name__)

FIELDS = [
    ('name',            'Full Name',           'text',     True,  []),
    ('phone',           'Phone',               'text',     False, []),
    ('email',           'Email',               'email',    False, []),
    ('passport_number', 'Passport Number',     'text',     False, []),
    ('nationality',     'Nationality',         'text',     False, []),
    ('date_of_birth',   'Date of Birth',       'date',     False, []),
    ('address',         'Address',             'text',     False, []),
    ('company_name',    'Company / Employer',  'text',     False, []),
    ('notes',           'Notes',               'textarea', False, []),
]

@customers_bp.route('/')
def index():
    q = request.args.get('q', '')
    recs = search('customers', q, ['name','phone','email','passport_number','nationality']) if q else get_all('customers')
    recs = sorted(recs, key=lambda x: x.get('created_at',''), reverse=True)
    return render_template('pages/customers/index.html', records=recs, q=q, fields=FIELDS, delete_fn='customers.delete_customer')

@customers_bp.route('/new', methods=['GET','POST'])
def new():
    if request.method == 'POST':
        insert('customers', {f[0]: request.form.get(f[0],'') for f in FIELDS})
        flash('Customer added.', 'success')
        return redirect(url_for('customers.index'))
    return render_template('pages/customers/form.html', record={}, fields=FIELDS, is_edit=False)

@customers_bp.route('/<id>/edit', methods=['GET','POST'])
def edit(id):
    rec = get_by_id('customers', id)
    if not rec:
        flash('Customer not found.', 'danger')
        return redirect(url_for('customers.index'))
    if request.method == 'POST':
        update('customers', id, {f[0]: request.form.get(f[0],'') for f in FIELDS})
        flash('Customer updated.', 'success')
        return redirect(url_for('customers.index'))
    return render_template('pages/customers/form.html', record=rec, fields=FIELDS, is_edit=True)

@customers_bp.route('/<id>/delete', methods=['POST'])
def delete_customer(id):
    delete('customers', id)
    flash('Customer deleted.', 'success')
    return redirect(url_for('customers.index'))
