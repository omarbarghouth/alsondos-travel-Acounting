from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_all, get_by_id, insert, update, delete, search

companies_bp = Blueprint('companies', __name__)

FIELDS = [
    ('name',           'Company Name',           'text',     True,  []),
    ('contact_name',   'Contact Person',         'text',     False, []),
    ('phone',          'Phone',                  'text',     False, []),
    ('email',          'Email',                  'email',    False, []),
    ('address',        'Address',                'text',     False, []),
    ('city',           'City',                   'text',     False, []),
    ('country',        'Country',                'text',     False, []),
    ('tax_number',     'Tax / Registration No.', 'text',     False, []),
    ('credit_limit',   'Credit Limit (JOD)',     'number',   False, []),
    ('payment_terms',  'Payment Terms',          'text',     False, []),
    ('notes',          'Notes',                  'textarea', False, []),
]

@companies_bp.route('/')
def index():
    q = request.args.get('q', '')
    recs = search('companies', q, ['name','contact_name','city','email']) if q else get_all('companies')
    recs = sorted(recs, key=lambda x: x.get('created_at',''), reverse=True)
    return render_template('pages/companies/index.html', records=recs, q=q, fields=FIELDS, delete_fn='companies.delete_company')

@companies_bp.route('/new', methods=['GET','POST'])
def new():
    if request.method == 'POST':
        insert('companies', {f[0]: request.form.get(f[0],'') for f in FIELDS})
        flash('Company added.', 'success')
        return redirect(url_for('companies.index'))
    return render_template('pages/companies/form.html', record={}, fields=FIELDS, is_edit=False)

@companies_bp.route('/<id>/edit', methods=['GET','POST'])
def edit(id):
    rec = get_by_id('companies', id)
    if not rec:
        flash('Company not found.', 'danger')
        return redirect(url_for('companies.index'))
    if request.method == 'POST':
        update('companies', id, {f[0]: request.form.get(f[0],'') for f in FIELDS})
        flash('Company updated.', 'success')
        return redirect(url_for('companies.index'))
    return render_template('pages/companies/form.html', record=rec, fields=FIELDS, is_edit=True)

@companies_bp.route('/<id>/delete', methods=['POST'])
def delete_company(id):
    delete('companies', id)
    flash('Company deleted.', 'success')
    return redirect(url_for('companies.index'))
