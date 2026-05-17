from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_all, get_by_id, insert, update, delete, next_number

transactions_bp = Blueprint('transactions', __name__)

STATUSES      = ['Confirmed', 'Pending', 'Cancelled', 'Refunded']
SERVICE_TYPES = ['Flight', 'Hotel', 'Package', 'Visa', 'Transfer', 'Tour', 'Transportation', 'Insurance']
TRIP_TYPES    = ['Round Trip', 'One Way']
MEAL_PLANS    = ['Bed & Breakfast', 'Half Board', 'Full Board', 'All Inclusive', 'Room Only']
ROOM_TYPES    = ['Standard', 'Deluxe', 'Superior', 'Suite', 'Twin', 'Family', 'Studio']
VEHICLE_TYPES = ['Sedan', 'SUV', 'Van', 'Minibus', 'Bus', 'Limousine']
VISA_TYPES    = ['Tourist', 'Business', 'Transit', 'Student', 'Work', 'Residence']

def _refs():
    return dict(
        suppliers    = get_all('suppliers'),
        companies    = get_all('companies'),
        customers    = get_all('customers'),
        hotels       = get_all('hotels'),
        tours        = get_all('tours'),
        transfers    = get_all('transfers'),
        statuses     = STATUSES,
        service_types= SERVICE_TYPES,
        trip_types   = TRIP_TYPES,
        meal_plans   = MEAL_PLANS,
        room_types   = ROOM_TYPES,
        vehicle_types= VEHICLE_TYPES,
        visa_types   = VISA_TYPES,
    )

@transactions_bp.route('/')
def index():
    txns   = get_all('transactions')
    q      = request.args.get('q', '').lower()
    status = request.args.get('status', '')
    stype  = request.args.get('service_type', '')
    date_f = request.args.get('date_from', '')
    date_t = request.args.get('date_to', '')

    if q:
        txns = [t for t in txns if
                q in (t.get('ref_number')    or '').lower() or
                q in (t.get('customer_name') or '').lower() or
                q in (t.get('sell_to')       or '').lower()]
    if status: txns = [t for t in txns if t.get('status')       == status]
    if stype:  txns = [t for t in txns if t.get('service_type') == stype]
    if date_f: txns = [t for t in txns if (t.get('booking_date') or '') >= date_f]
    if date_t: txns = [t for t in txns if (t.get('booking_date') or '') <= date_t]

    txns = sorted(txns, key=lambda x: x.get('created_at', ''), reverse=True)
    return render_template('pages/transactions/index.html',
                           transactions=txns, statuses=STATUSES,
                           service_types=SERVICE_TYPES,
                           q=q, status=status, stype=stype,
                           date_f=date_f, date_t=date_t)

@transactions_bp.route('/new', methods=['GET', 'POST'])
def new():
    refs = _refs()
    if request.method == 'POST':
        data = _collect()
        if not data.get('service_type'):
            flash('Please select a service type.', 'danger')
            return render_template('pages/transactions/form.html', txn=data, **refs, is_edit=False)
        data['ref_number'] = next_number('transactions', 'TXN')
        rec = insert('transactions', data)
        flash(f"Transaction {rec['ref_number']} created successfully.", 'success')
        return redirect(url_for('transactions.view', id=rec['id']))
    return render_template('pages/transactions/form.html', txn={}, **refs, is_edit=False)

@transactions_bp.route('/<id>')
def view(id):
    txn = get_by_id('transactions', id)
    if not txn:
        flash('Transaction not found.', 'danger')
        return redirect(url_for('transactions.index'))
    pays      = [p for p in get_all('payments') if p.get('transaction_id') == id]
    total_paid= sum(float(p.get('amount') or 0) for p in pays)
    remaining = float(txn.get('sell_price') or 0) - total_paid
    return render_template('pages/transactions/view.html',
                           txn=txn, payments=pays,
                           total_paid=total_paid, remaining=remaining)

@transactions_bp.route('/<id>/edit', methods=['GET', 'POST'])
def edit(id):
    txn  = get_by_id('transactions', id)
    if not txn:
        flash('Transaction not found.', 'danger')
        return redirect(url_for('transactions.index'))
    refs = _refs()
    if request.method == 'POST':
        update('transactions', id, _collect())
        flash('Transaction updated successfully.', 'success')
        return redirect(url_for('transactions.view', id=id))
    return render_template('pages/transactions/form.html', txn=txn, **refs, is_edit=True)

@transactions_bp.route('/<id>/delete', methods=['POST'])
def delete_txn(id):
    txn = get_by_id('transactions', id)
    ref = (txn or {}).get('ref_number', id)
    delete('transactions', id)
    flash(f'Transaction {ref} deleted.', 'success')
    return redirect(url_for('transactions.index'))

@transactions_bp.route('/<id>/print')
def print_txn(id):
    txn = get_by_id('transactions', id)
    if not txn:
        flash('Transaction not found.', 'danger')
        return redirect(url_for('transactions.index'))
    return render_template('pages/transactions/print.html', txn=txn)

def _f(key, default=''):
    return request.form.get(key, default)

def _flt(key):
    try: return float(request.form.get(key) or 0)
    except: return 0.0

def _collect() -> dict:
    sell   = _flt('sell_price')
    cost   = _flt('net_cost')
    return {
        'service_type':      _f('service_type'),
        'booking_date':      _f('booking_date'),
        'status':            _f('status', 'Pending'),
        'trip_type':         _f('trip_type'),
        'from_city':         _f('from_city'),
        'to_city':           _f('to_city'),
        'departure_date':    _f('departure_date'),
        'return_date':       _f('return_date'),
        # Customer
        'customer_name':     _f('customer_name'),
        'customer_phone':    _f('customer_phone'),
        'passport_number':   _f('passport_number'),
        'nationality':       _f('nationality'),
        'customer_id':       _f('customer_id'),
        # Supplier
        'supplier_name':     _f('supplier_name'),
        'buy_from':          _f('buy_from'),
        'return_supplier':   _f('return_supplier'),
        'supplier_id':       _f('supplier_id'),
        # Sales
        'sell_to':           _f('sell_to'),
        'company_id':        _f('company_id'),
        'net_cost':          cost,
        'sell_price':        sell,
        'profit':            round(sell - cost, 3),
        # Hotel
        'hotel_name':        _f('hotel_name'),
        'hotel_id':          _f('hotel_id'),
        'room_type':         _f('room_type'),
        'meal_plan':         _f('meal_plan'),
        'hotel_checkin':     _f('hotel_checkin'),
        'hotel_checkout':    _f('hotel_checkout'),
        'hotel_nights':      _f('hotel_nights'),
        'num_rooms':         _f('num_rooms'),
        # Flight
        'airline':           _f('airline'),
        'flight_route':      _f('flight_route'),
        'pnr':               _f('pnr'),
        'baggage':           _f('baggage'),
        # Transfer
        'transfer_type':     _f('transfer_type'),
        'pickup_time':       _f('pickup_time'),
        'vehicle_type':      _f('vehicle_type'),
        'driver_contact':    _f('driver_contact'),
        'arrival_flight':    _f('arrival_flight'),
        'pickup_sign':       _f('pickup_sign'),
        # Tour
        'tour_name':         _f('tour_name'),
        'tour_id':           _f('tour_id'),
        'tour_date':         _f('tour_date'),
        'tour_included':     _f('tour_included'),
        # Visa
        'visa_type':         _f('visa_type'),
        'visa_status':       _f('visa_status'),
        # Insurance
        'insurance_type':    _f('insurance_type'),
        'insurance_period':  _f('insurance_period'),
        # Notes
        'notes':             _f('notes'),
    }
