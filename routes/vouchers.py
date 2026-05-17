from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_all, get_by_id, insert, update, delete, next_number

vouchers_bp = Blueprint('vouchers', __name__)

MEAL_PLANS = ['Bed & Breakfast','Half Board','Full Board','All Inclusive','Room Only']
ROOM_TYPES = ['Standard','Deluxe','Superior','Suite','Twin','Family','Studio']

@vouchers_bp.route('/')
def index():
    vch = sorted(get_all('vouchers'), key=lambda x: x.get('created_at',''), reverse=True)
    return render_template('pages/vouchers/index.html', vouchers=vch)

@vouchers_bp.route('/new', methods=['GET','POST'])
def new():
    if request.method == 'POST':
        data = _collect()
        data['voucher_number'] = next_number('vouchers', 'VCH')
        rec = insert('vouchers', data)
        flash(f"Voucher {rec['voucher_number']} created.", 'success')
        return redirect(url_for('vouchers.print_voucher', id=rec['id']))
    return render_template('pages/vouchers/form.html',
                           voucher={}, is_edit=False,
                           hotels=get_all('hotels'), customers=get_all('customers'),
                           txns=get_all('transactions'), transfers=get_all('transfers'),
                           tours=get_all('tours'), meal_plans=MEAL_PLANS, room_types=ROOM_TYPES)

@vouchers_bp.route('/<id>/edit', methods=['GET','POST'])
def edit(id):
    vch = get_by_id('vouchers', id)
    if not vch:
        flash('Voucher not found.', 'danger')
        return redirect(url_for('vouchers.index'))
    if request.method == 'POST':
        update('vouchers', id, _collect())
        flash('Voucher updated.', 'success')
        return redirect(url_for('vouchers.print_voucher', id=id))
    return render_template('pages/vouchers/form.html',
                           voucher=vch, is_edit=True,
                           hotels=get_all('hotels'), customers=get_all('customers'),
                           txns=get_all('transactions'), transfers=get_all('transfers'),
                           tours=get_all('tours'), meal_plans=MEAL_PLANS, room_types=ROOM_TYPES)

@vouchers_bp.route('/<id>/print')
def print_voucher(id):
    vch = get_by_id('vouchers', id)
    if not vch:
        flash('Voucher not found.', 'danger')
        return redirect(url_for('vouchers.index'))
    return render_template('pages/vouchers/print.html', voucher=vch)

@vouchers_bp.route('/<id>/delete', methods=['POST'])
def delete_voucher(id):
    delete('vouchers', id)
    flash('Voucher deleted.', 'success')
    return redirect(url_for('vouchers.index'))

def _collect():
    f = request.form.get
    return {
        'transaction_id':     f('transaction_id',''),
        'guest_name':         f('guest_name',''),
        'num_guests':         f('num_guests',''),
        'hotel_name':         f('hotel_name',''),
        'hotel_address':      f('hotel_address',''),
        'hotel_contact':      f('hotel_contact',''),
        'hotel_phone':        f('hotel_phone',''),
        'room_type':          f('room_type',''),
        'meal_plan':          f('meal_plan',''),
        'checkin':            f('checkin',''),
        'checkout':           f('checkout',''),
        'nights':             f('nights',''),
        'include_transfer':   f('include_transfer',''),
        'include_tours':      f('include_tours',''),
        'include_insurance':  f('include_insurance',''),
        'arrival_flight':     f('arrival_flight',''),
        'pickup_sign':        f('pickup_sign',''),
        'driver_contact':     f('driver_contact',''),
        'pickup_time':        f('pickup_time',''),
        'vehicle_type':       f('vehicle_type',''),
        'emergency_contact':  f('emergency_contact',''),
        'cancellation_policy':f('cancellation_policy',''),
        'remarks':            f('remarks',''),
    }
