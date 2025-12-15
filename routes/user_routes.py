"""
User Routes - API endpoints for user management
Supports both Supabase and local authentication
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import os

# Try to import Supabase service first
try:
    from services.supabase_service import supabase_service
    USE_SUPABASE = supabase_service.is_available and os.getenv('USE_SUPABASE', 'true').lower() == 'true'
except ImportError:
    USE_SUPABASE = False
    supabase_service = None

from services import UserService

user_bp = Blueprint('user', __name__)
user_service = UserService()


def auth_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Try Supabase first
        if USE_SUPABASE and supabase_service:
            user_id = supabase_service.validate_token(token)
        else:
            user_id = user_service.validate_token(token)
        
        if not user_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.user_id = user_id
        return f(*args, **kwargs)
    return decorated


@user_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json
        
        email = data.get('email')
        password = data.get('password')
        username = data.get('username', email.split('@')[0] if email else None)
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Use Supabase if available
        if USE_SUPABASE and supabase_service:
            result = supabase_service.register(
                email=email,
                password=password,
                username=username,
                display_name=data.get('display_name'),
                role=data.get('role', 'student')
            )
        else:
            result = user_service.register(
                username=username,
                email=email,
                password=password,
                display_name=data.get('display_name'),
                role=data.get('role', 'student')
            )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.json
        
        email = data.get('email') or data.get('username')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email/username and password required'}), 400
        
        # Use Supabase if available
        if USE_SUPABASE and supabase_service:
            result = supabase_service.login(
                email=email,
                password=password
            )
        else:
            result = user_service.login(
                username=email,
                password=password
            )
        
        if 'error' in result:
            return jsonify(result), 401
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/logout', methods=['POST'])
@auth_required
def logout():
    """Logout user"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if USE_SUPABASE and supabase_service:
            result = supabase_service.logout(token)
        else:
            result = user_service.logout(token)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/me', methods=['GET'])
@auth_required
def get_current_user():
    """Get current user info"""
    try:
        if USE_SUPABASE and supabase_service:
            user = supabase_service.get_user_profile(request.user_id)
        else:
            user = user_service.get_user(request.user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/profile', methods=['PUT'])
@auth_required
def update_profile():
    """Update user profile"""
    try:
        data = request.json
        
        if USE_SUPABASE and supabase_service:
            result = supabase_service.update_user_profile(
                user_id=request.user_id,
                display_name=data.get('display_name'),
                avatar_url=data.get('avatar_url')
            )
        else:
            result = user_service.update_profile(
                user_id=request.user_id,
                display_name=data.get('display_name'),
                email=data.get('email'),
                avatar_url=data.get('avatar_url'),
                bio=data.get('bio')
            )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh access token"""
    try:
        data = request.json
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return jsonify({'error': 'Refresh token required'}), 400
        
        if USE_SUPABASE and supabase_service:
            result = supabase_service.refresh_session(refresh_token)
        else:
            return jsonify({'error': 'Token refresh not available'}), 400
        
        if 'error' in result:
            return jsonify(result), 401
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/password', methods=['PUT'])
@auth_required
def change_password():
    """Change user password"""
    try:
        data = request.json
        
        if not data.get('old_password') or not data.get('new_password'):
            return jsonify({'error': 'Old and new password required'}), 400
        
        result = user_service.change_password(
            user_id=request.user_id,
            old_password=data['old_password'],
            new_password=data['new_password']
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/password/reset-request', methods=['POST'])
def request_password_reset():
    """Request password reset"""
    try:
        data = request.json
        
        if not data.get('email'):
            return jsonify({'error': 'Email required'}), 400
        
        result = user_service.request_password_reset(data['email'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/password/reset', methods=['POST'])
def reset_password():
    """Reset password with token"""
    try:
        data = request.json
        
        if not data.get('token') or not data.get('new_password'):
            return jsonify({'error': 'Token and new password required'}), 400
        
        result = user_service.reset_password(
            reset_token=data['token'],
            new_password=data['new_password']
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/preferences', methods=['GET'])
@auth_required
def get_preferences():
    """Get user preferences"""
    try:
        preferences = user_service.get_preferences(request.user_id)
        return jsonify(preferences)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/preferences', methods=['PUT'])
@auth_required
def update_preferences():
    """Update user preferences"""
    try:
        data = request.json
        
        result = user_service.update_preferences(request.user_id, data)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/stats', methods=['GET'])
@auth_required
def get_stats():
    """Get user statistics"""
    try:
        stats = user_service.get_user_stats(request.user_id)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/history', methods=['GET'])
@auth_required
def get_history():
    """Get quiz history"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        history = user_service.get_quiz_history(request.user_id, page, per_page)
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/saved', methods=['GET'])
@auth_required
def get_saved_quizzes():
    """Get saved quizzes"""
    try:
        saved = user_service.get_saved_quizzes(request.user_id)
        return jsonify({'saved': saved})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/saved/<quiz_id>', methods=['POST'])
@auth_required
def save_quiz(quiz_id):
    """Save/bookmark a quiz"""
    try:
        result = user_service.save_quiz(request.user_id, quiz_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/saved/<quiz_id>', methods=['DELETE'])
@auth_required
def unsave_quiz(quiz_id):
    """Remove quiz from saved"""
    try:
        result = user_service.unsave_quiz(request.user_id, quiz_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Teacher routes
@user_bp.route('/class', methods=['POST'])
@auth_required
def create_class():
    """Create a class (teacher only)"""
    try:
        data = request.json
        
        result = user_service.create_class(
            teacher_id=request.user_id,
            class_name=data.get('name'),
            description=data.get('description')
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/class/join', methods=['POST'])
@auth_required
def join_class():
    """Join a class using code"""
    try:
        data = request.json
        
        if not data.get('code'):
            return jsonify({'error': 'Class code required'}), 400
        
        result = user_service.join_class(request.user_id, data['code'])
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/class/<class_id>/students', methods=['GET'])
@auth_required
def get_class_students(class_id):
    """Get students in a class"""
    try:
        students = user_service.get_class_students(request.user_id, class_id)
        return jsonify({'students': students})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
