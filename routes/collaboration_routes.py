"""
Collaboration Routes - API endpoints for real-time quizzes
"""

from flask import Blueprint, request, jsonify
from services import CollaborationService

collaboration_bp = Blueprint('collaboration', __name__)
collaboration_service = CollaborationService()


# ==================== Quiz Sharing ====================

@collaboration_bp.route('/share', methods=['POST'])
def create_share_link():
    """Create a shareable link for a quiz"""
    try:
        data = request.json
        
        result = collaboration_service.create_share_link(
            quiz_id=data.get('quiz_id'),
            user_id=data.get('user_id'),
            password=data.get('password'),
            max_attempts=data.get('max_attempts'),
            expires_in_days=data.get('expires_in_days'),
            allow_review=data.get('allow_review', True),
            show_leaderboard=data.get('show_leaderboard', True),
            randomize_questions=data.get('randomize_questions', False)
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@collaboration_bp.route('/shared/<share_code>', methods=['GET'])
def get_shared_quiz(share_code):
    """Access a shared quiz"""
    try:
        password = request.args.get('password')
        
        result = collaboration_service.get_shared_quiz(share_code, password)
        
        if not result:
            return jsonify({'error': 'Share link not found'}), 404
        
        if 'error' in result:
            if result.get('password_required'):
                return jsonify(result), 401
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Real-time Quiz Rooms ====================

@collaboration_bp.route('/room', methods=['POST'])
def create_room():
    """Create a real-time quiz room"""
    try:
        data = request.json
        
        result = collaboration_service.create_room(
            quiz_id=data.get('quiz_id'),
            host_id=data.get('host_id'),
            name=data.get('name'),
            max_participants=data.get('max_participants', 50),
            question_time_limit=data.get('question_time_limit', 30),
            scheduled_start=data.get('scheduled_start')
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@collaboration_bp.route('/room/<room_code>/join', methods=['POST'])
def join_room(room_code):
    """Join a quiz room"""
    try:
        data = request.json
        
        result = collaboration_service.join_room(
            room_code=room_code,
            user_id=data.get('user_id'),
            nickname=data.get('nickname'),
            avatar_emoji=data.get('avatar_emoji')
        )
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@collaboration_bp.route('/room/<room_code>/start', methods=['POST'])
def start_room(room_code):
    """Start a quiz room (host only)"""
    try:
        data = request.json
        host_id = data.get('host_id')
        
        result = collaboration_service.start_room(room_code, host_id)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@collaboration_bp.route('/room/<room_code>/answer', methods=['POST'])
def submit_answer(room_code):
    """Submit answer in real-time room"""
    try:
        data = request.json
        
        result = collaboration_service.submit_room_answer(
            room_code=room_code,
            participant_id=data.get('participant_id'),
            question_index=data.get('question_index'),
            answer=data.get('answer'),
            time_ms=data.get('time_ms', 0)
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@collaboration_bp.route('/room/<room_code>/next', methods=['POST'])
def next_question(room_code):
    """Move to next question (host only)"""
    try:
        data = request.json
        host_id = data.get('host_id')
        
        result = collaboration_service.next_question(room_code, host_id)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@collaboration_bp.route('/room/<room_code>/leaderboard', methods=['GET'])
def get_room_leaderboard(room_code):
    """Get current room leaderboard"""
    try:
        leaderboard = collaboration_service.get_room_leaderboard(room_code)
        return jsonify({'leaderboard': leaderboard})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@collaboration_bp.route('/room/<room_code>/end', methods=['POST'])
def end_room(room_code):
    """End a quiz room"""
    try:
        result = collaboration_service.end_room(room_code)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Global Leaderboard ====================

@collaboration_bp.route('/leaderboard', methods=['GET'])
def get_global_leaderboard():
    """Get global leaderboard"""
    try:
        leaderboard_type = request.args.get('type', 'global')
        limit = request.args.get('limit', 100, type=int)
        
        leaderboard = collaboration_service.get_global_leaderboard(
            leaderboard_type=leaderboard_type,
            limit=limit
        )
        
        return jsonify({'leaderboard': leaderboard})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@collaboration_bp.route('/leaderboard/update', methods=['POST'])
def update_leaderboard():
    """Update global leaderboard entry"""
    try:
        data = request.json
        
        result = collaboration_service.update_global_leaderboard(
            user_id=data.get('user_id'),
            nickname=data.get('nickname'),
            score=data.get('score', 0),
            quiz_id=data.get('quiz_id')
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
