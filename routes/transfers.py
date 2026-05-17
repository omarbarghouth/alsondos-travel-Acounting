from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_all, get_by_id, insert, update, delete, search

transfers_bp = Blueprint('transfers', __name__)

FIELDS = [
    ('name',         'Route / Name',    'text',   True,  []),
    ('from_location','From',            'text',   False, []),
    ('to_location',  'To',              'text',   False, []),
    ('vehicle_type', 'Vehicle Type',    'select', False, ['Sedan','SUV','Van','Minibus','Bus','Limousine']),
    ('capacity',     'Capacity (pax)',  'number', False, []),
    ('price_jod',    'Price (JOD)',     'number', False, []),
    ('driver_name',  'Driver Name',     'text',   False, []),
    ('driver_phone', 'Driver Phone',    'text',   False, []),
    ('notes',        'Notes',           'textarea',False,[]),
]

@transfers_bp.route('/')
def index():
    q = request.args.get('q', '')
    recs = search('transfers', q, ['name','from_location','to_location','vehicle_type']) if q else get_all('transfers')
    recs = sorted(recs, key=lambda x: x.get('created_at',''), reverse=True)
    return render_template('pages/transfers/index.html', records=recs, q=q, fields=FIELDS, delete_fn='transfers.delete_transfer')

@transfers_bp.route('/new', methods=['GET','POST'])
def new():
    if request.method == 'POST':
        insert('transfers', {f[0]: request.form.get(f[0],'') for f in FIELDS})
        flash('Transfer added.', 'success')
        return redirect(url_for('transfers.index'))
    return render_template('pages/transfers/form.html', record={}, fields=FIELDS, is_edit=False)

@transfers_bp.route('/<id>/edit', methods=['GET','POST'])
def edit(id):
    rec = get_by_id('transfers', id)
    if not rec:
        flash('Transfer not found.', 'danger')
        return redirect(url_for('transfers.index'))
    if request.method == 'POST':
        update('transfers', id, {f[0]: request.form.get(f[0],'') for f in FIELDS})
        flash('Transfer updated.', 'success')
        return redirect(url_for('transfers.index'))
    return render_template('pages/transfers/form.html', record=rec, fields=FIELDS, is_edit=True)

@transfers_bp.route('/<id>/delete', methods=['POST'])
def delete_transfer(id):
    delete('transfers', id)
    flash('Transfer deleted.', 'success')
    return redirect(url_for('transfers.index'))
