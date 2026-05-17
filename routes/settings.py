import json, os
from flask import Blueprint, render_template, request, redirect, url_for, flash

settings_bp = Blueprint('settings', __name__)

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'settings.json')

DEFAULTS = {
    'agency_name':           'Alsondos Travel & Tourism',
    'address':               'Amman, Jordan',
    'phone':                 '',
    'email':                 '',
    'tax_number':            '',
    'website':               '',
    'currency': 'JOD',
    'invoice_footer':        'Thank you for choosing Alsondos Travel & Tourism.',
    'voucher_emergency':     '',
    'cancellation_policy':   '',
}

def load():
    try:
        with open(SETTINGS_FILE) as f:
            s = DEFAULTS.copy()
            s.update(json.load(f))
            return s
    except:
        return DEFAULTS.copy()

def save(data):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@settings_bp.route('/', methods=['GET','POST'])
def index():
    settings = load()
    if request.method == 'POST':
        for key in DEFAULTS:
            if key in request.form:
                settings[key] = request.form[key]
        save(settings)
        flash('Settings saved.', 'success')
        return redirect(url_for('settings.index'))
    return render_template('pages/settings/index.html', settings=settings)
