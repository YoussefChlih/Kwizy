"""
Authentication Routes
Handles login, signup, and user management endpoints
"""

from flask import Blueprint, request, jsonify, session
from functools import wraps
import logging
from auth_service import AuthService

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
auth_service = AuthService()


def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Non authentifié'}), 401
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        missing = [f for f in required_fields if not data.get(f)]
        
        if missing:
            return jsonify({
                'success': False,
                'error': f'Champs obligatoires manquants: {", ".join(missing)}'
            }), 400
        
        # Password validation
        password = data.get('password')
        if len(password) < 8:
            return jsonify({
                'success': False,
                'error': 'Le mot de passe doit contenir au moins 8 caractères'
            }), 400
        
        if not any(c.isupper() for c in password):
            return jsonify({
                'success': False,
                'error': 'Le mot de passe doit contenir au moins une majuscule'
            }), 400
        
        if not any(c.isdigit() for c in password):
            return jsonify({
                'success': False,
                'error': 'Le mot de passe doit contenir au moins un chiffre'
            }), 400
        
        # Perform signup
        user_data = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'company': data.get('company', ''),
            'job_title': data.get('job_title', ''),
            'language': data.get('language', 'fr'),
            'timezone': data.get('timezone', 'Europe/Paris')
        }
        
        success, message, user_info = auth_service.signup(
            data.get('email'),
            password,
            user_data
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'user': user_info
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
    
    except Exception as e:
        logger.error(f"Signup error: {e}")
        return jsonify({
            'success': False,
            'error': f'Erreur serveur: {str(e)}'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email et mot de passe requis'
            }), 400
        
        success, message, session_data = auth_service.login(email, password)
        
        if success:
            # Store user data in session
            session['user_id'] = session_data['user_id']
            session['email'] = session_data['email']
            session['profile'] = session_data['profile']
            
            return jsonify({
                'success': True,
                'message': message,
                'user': {
                    'id': session_data['user_id'],
                    'email': session_data['email'],
                    'profile': session_data['profile']
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 401
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({
            'success': False,
            'error': f'Erreur serveur: {str(e)}'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout user"""
    try:
        user_id = session.get('user_id')
        auth_service.logout(user_id)
        
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Déconnexion réussie'
        }), 200
    
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({
            'success': False,
            'error': f'Erreur: {str(e)}'
        }), 500


@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get current user profile"""
    try:
        user_id = session.get('user_id')
        profile = auth_service.get_user_profile(user_id)
        
        if profile:
            return jsonify({
                'success': True,
                'profile': profile
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Profil non trouvé'
            }), 404
    
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return jsonify({
            'success': False,
            'error': f'Erreur: {str(e)}'
        }), 500


@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        user_id = session.get('user_id')
        data = request.get_json()
        
        # Only allow certain fields to be updated
        allowed_fields = [
            'first_name', 'last_name', 'company', 'job_title',
            'timezone', 'avatar_url', 'preferences'
        ]
        
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        success, message = auth_service.update_user_profile(user_id, update_data)
        
        if success:
            # Update session
            session['profile'] = auth_service.get_user_profile(user_id)
            
            return jsonify({
                'success': True,
                'message': message
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
    
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        return jsonify({
            'success': False,
            'error': f'Erreur: {str(e)}'
        }), 500


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email requis'
            }), 400
        
        success, message = auth_service.reset_password(email)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
    
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        return jsonify({
            'success': False,
            'error': f'Erreur: {str(e)}'
        }), 500


@auth_bp.route('/check-session', methods=['GET'])
def check_session():
    """Check if user is logged in"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session.get('user_id'),
                'email': session.get('email'),
                'profile': session.get('profile')
            }
        }), 200
    else:
        return jsonify({
            'authenticated': False
        }), 200
