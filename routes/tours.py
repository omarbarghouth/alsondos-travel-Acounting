from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_all, get_by_id, insert, update, delete, search

tours_bp = Blueprint('tours', __name__)

FIELDS = [
    ('name',        'Tour Name',       'text',     True,  []),
    ('destination', 'Destination',     'text',     False, []),
    ('duration',    'Duration (days)', 'number',   False, []),
    ('operator',    'Tour Operator',   'text',     False, []),
    ('price_jod',   'Price (JOD)',     'number',   False, []),
    ('inclusions',  'Inclusions',      'textarea', False, []),
    ('exclusions',  'Exclusions',      'textarea', False, []),
    ('notes',       'Notes',           'textarea', False, []),
]

@tours_bp.route('/')
def index():
    q = request.args.get('q', '')
    recs = search('tours', q, ['name','destination','operator']) if q else get_all('tours')
    recs = sorted(recs, key=lambda x: x.get('created_at',''), reverse=True)
    return render_template('pages/tours/index.html', records=recs, q=q, fields=FIELDS, delete_fn='tours.delete_tour')

@tours_bp.route('/new', methods=['GET','POST'])
def new():
    if request.method == 'POST':
        insert('tours', {f[0]: request.form.get(f[0],'') for f in FIELDS})
        flash('Tour added.', 'success')
        return redirect(url_for('tours.index'))
    return render_template('pages/tours/form.html', record={}, fields=FIELDS, is_edit=False)

@tours_bp.route('/<id>/edit', methods=['GET','POST'])
def edit(id):
    rec = get_by_id('tours', id)
    if not rec:
        flash('Tour not found.', 'danger')
        return redirect(url_for('tours.index'))
    if request.method == 'POST':
        update('tours', id, {f[0]: request.form.get(f[0],'') for f in FIELDS})
        flash('Tour updated.', 'success')
        return redirect(url_for('tours.index'))
    return render_template('pages/tours/form.html', record=rec, fields=FIELDS, is_edit=True)

@tours_bp.route('/<id>/delete', methods=['POST'])
def delete_tour(id):
    delete('tours', id)
    flash('Tour deleted.', 'success')
    return redirect(url_for('tours.index'))
