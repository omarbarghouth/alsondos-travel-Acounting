from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from mock_data import USERS

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def root():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = next((u for u in USERS if u['username'] == username and u['password'] == password), None)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['name'] = user['name']
            session['role'] = user['role']
            flash(f"Welcome back, {user['name']}!", 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    return render_template('pages/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
