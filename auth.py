from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

auth_bp = Blueprint('auth', __name__)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':  # Replace with proper authentication
            user = User(id=1)
            login_user(user)
            return redirect(url_for('routes.index'))
        else:
            return 'Invalid credentials'
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/protected')
@login_required
def protected():
    return 'Logged in as: ' + current_user.id
