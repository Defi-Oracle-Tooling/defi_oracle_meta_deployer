from flask import Blueprint, request, redirect, url_for, render_template, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_oauthlib.client import OAuth
import os
from datetime import datetime, timedelta
import jwt
from functools import wraps

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.session_protection = 'strong'

auth_bp = Blueprint('auth', __name__)
oauth = OAuth()

# Configure Azure AD OAuth
azure = oauth.remote_app(
    'azure',
    consumer_key=os.getenv('AZURE_CLIENT_ID'),
    consumer_secret=os.getenv('AZURE_CLIENT_SECRET'),
    request_token_params={'scope': 'openid email profile'},
    base_url=f'https://login.microsoftonline.com/{os.getenv("AZURE_TENANT_ID")}/oauth2/v2.0/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url=f'https://login.microsoftonline.com/{os.getenv("AZURE_TENANT_ID")}/oauth2/v2.0/token',
    authorize_url=f'https://login.microsoftonline.com/{os.getenv("AZURE_TENANT_ID")}/oauth2/v2.0/authorize'
)

class User(UserMixin):
    def __init__(self, id, email=None, roles=None):
        self.id = id
        self.email = email
        self.roles = roles or []
        self.authenticated = True
        self.active = True

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def has_role(self, role):
        return role in self.roles

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return {'message': 'Invalid token header'}, 401

        if not token:
            return {'message': 'Token is missing'}, 401

        try:
            data = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=["HS256"])
            current_user = User(id=data['user_id'], email=data.get('email'), roles=data.get('roles', []))
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401

        return f(current_user, *args, **kwargs)
    return decorated

def generate_token(user):
    token_data = {
        'user_id': user.id,
        'email': user.email,
        'roles': user.roles,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(token_data, os.getenv('JWT_SECRET_KEY'), algorithm='HS256')

@login_manager.user_loader
def load_user(user_id):
    # Implement user loading from your storage
    # This is a simple example - replace with your actual user storage
    stored_user = session.get('user_data')
    if stored_user and stored_user.get('id') == user_id:
        return User(
            id=stored_user['id'],
            email=stored_user.get('email'),
            roles=stored_user.get('roles', [])
        )
    return None

def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            if not any(current_user.has_role(role) for role in roles):
                return jsonify({'error': 'Insufficient permissions'}), 403
                
            return f(*args, **kwargs)
        return wrapped
    return wrapper

# Rate limiting decorator
def rate_limit(max_requests=100, window=60):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not hasattr(wrapped, '_requests'):
                wrapped._requests = []
            
            now = datetime.utcnow()
            wrapped._requests = [t for t in wrapped._requests if (now - t).seconds < window]
            
            if len(wrapped._requests) >= max_requests:
                return jsonify({'error': 'Rate limit exceeded'}), 429
                
            wrapped._requests.append(now)
            return f(*args, **kwargs)
        return wrapped
    return decorator

# Session security configuration
def configure_session_security(app):
    app.config.update(
        PERMANENT_SESSION_LIFETIME=timedelta(hours=1),
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax'
    )
    
    @app.before_request
    def make_session_permanent():
        session.permanent = True

@auth_bp.route('/login')
def login():
    return azure.authorize(callback=url_for('auth.authorized', _external=True))

@auth_bp.route('/login/authorized')
def authorized():
    try:
        resp = azure.authorized_response()
        if resp is None or resp.get('access_token') is None:
            return 'Access denied: reason={} error={}'.format(
                request.args['error_reason'],
                request.args['error_description']
            )
        
        # Get user info from Azure AD
        me = azure.get('me')
        user_data = {
            'id': me.data['id'],
            'email': me.data['mail'],
            'roles': me.data.get('roles', ['user'])  # Default role
        }
        
        # Store user data in session
        session['user_data'] = user_data
        
        # Create user object and log in
        user = User(
            id=user_data['id'],
            email=user_data['email'],
            roles=user_data['roles']
        )
        login_user(user)
        
        # Generate JWT token
        token = generate_token(user)
        
        # Store token in session
        session['jwt_token'] = token
        
        return redirect(url_for('routes.index'))
        
    except Exception as e:
        return f'Error: {str(e)}'

@auth_bp.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('auth.login'))

@azure.tokengetter
def get_azure_oauth_token():
    return session.get('azure_token')
