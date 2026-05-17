from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_all, get_by_id, insert, update, delete, search

hotels_bp = Blueprint('hotels', __name__)

FIELDS = [
    ('name',         'Hotel Name',    'text',     True,  []),
    ('stars',        'Stars',         'select',   False, ['1','2','3','4','5']),
    ('city',         'City',          'text',     False, []),
    ('country',      'Country',       'text',     False, []),
    ('address',      'Address',       'text',     False, []),
    ('contact_name', 'Contact Person','text',     False, []),
    ('phone',        'Phone',         'text',     False, []),
    ('email',        'Email',         'email',    False, []),
    ('website',      'Website',       'text',     False, []),
    ('facilities',   'Facilities',    'textarea', False, []),
    ('notes',        'Notes',         'textarea', False, []),
]

@hotels_bp.route('/')
def index():
    q = request.args.get('q', '')
    recs = search('hotels', q, ['name','city','country']) if q else get_all('hotels')
    recs = sorted(recs, key=lambda x: x.get('created_at',''), reverse=True)
    return render_template('pages/hotels/index.html', records=recs, q=q, fields=FIELDS, delete_fn='hotels.delete_hotel')

@hotels_bp.route('/new', methods=['GET','POST'])
def new():
    if request.method == 'POST':
        insert('hotels', {f[0]: request.form.get(f[0],'') for f in FIELDS})
        flash('Hotel added.', 'success')
        return redirect(url_for('hotels.index'))
    return render_template('pages/hotels/form.html', record={}, fields=FIELDS, is_edit=False)

@hotels_bp.route('/<id>/edit', methods=['GET','POST'])
def edit(id):
    rec = get_by_id('hotels', id)
    if not rec:
        flash('Hotel not found.', 'danger')
        return redirect(url_for('hotels.index'))
    if request.method == 'POST':
        update('hotels', id, {f[0]: request.form.get(f[0],'') for f in FIELDS})
        flash('Hotel updated.', 'success')
        return redirect(url_for('hotels.index'))
    return render_template('pages/hotels/form.html', record=rec, fields=FIELDS, is_edit=True)

@hotels_bp.route('/<id>/delete', methods=['POST'])
def delete_hotel(id):
    delete('hotels', id)
    flash('Hotel deleted.', 'success')
    return redirect(url_for('hotels.index'))
