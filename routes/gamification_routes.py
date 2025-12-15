"""
Gamification Routes - API endpoints for badges, streaks, challenges
"""

from flask import Blueprint, request, jsonify
from services import GamificationService

gamification_bp = Blueprint('gamification', __name__)
gamification_service = GamificationService()


# ==================== Points & XP ====================

@gamification_bp.route('/award-points', methods=['POST'])
def award_points():
    """Award points for an activity"""
    try:
        data = request.json
        
        result = gamification_service.award_points(
            user_id=data.get('user_id'),
            activity_type=data.get('activity_type'),
            score=data.get('score'),
            perfect=data.get('perfect', False),
            streak=data.get('streak', 1)
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gamification_bp.route('/user/<user_id>/xp', methods=['GET'])
def get_user_xp(user_id):
    """Get user XP and level info"""
    try:
        xp_info = gamification_service.get_user_xp(user_id)
        return jsonify(xp_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Badges ====================

@gamification_bp.route('/badges', methods=['GET'])
def get_all_badges():
    """Get all available badges"""
    try:
        badges = gamification_service.get_all_badges()
        return jsonify({'badges': badges})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gamification_bp.route('/user/<user_id>/badges', methods=['GET'])
def get_user_badges(user_id):
    """Get user's earned badges"""
    try:
        badges = gamification_service.get_user_badges(user_id)
        return jsonify({'badges': badges})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gamification_bp.route('/check-badges', methods=['POST'])
def check_badges():
    """Check and award any new badges"""
    try:
        data = request.json
        
        new_badges = gamification_service.check_and_award_badges(
            user_id=data.get('user_id'),
            context=data.get('context', {})
        )
        
        return jsonify({'new_badges': new_badges})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Streaks ====================

@gamification_bp.route('/user/<user_id>/streak', methods=['GET'])
def get_user_streak(user_id):
    """Get user streak info"""
    try:
        streak = gamification_service.get_user_streak(user_id)
        return jsonify(streak)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gamification_bp.route('/user/<user_id>/streak/update', methods=['POST'])
def update_streak(user_id):
    """Update user streak (called after activity)"""
    try:
        result = gamification_service.update_streak(user_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Challenges ====================

@gamification_bp.route('/challenges/daily', methods=['GET'])
def get_daily_challenges():
    """Get today's daily challenges"""
    try:
        user_id = request.args.get('user_id')
        
        challenges = gamification_service.get_daily_challenges(user_id)
        return jsonify({'challenges': challenges})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gamification_bp.route('/challenges/weekly', methods=['GET'])
def get_weekly_challenges():
    """Get weekly challenges"""
    try:
        user_id = request.args.get('user_id')
        
        challenges = gamification_service.get_weekly_challenges(user_id)
        return jsonify({'challenges': challenges})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gamification_bp.route('/challenge/<challenge_id>/progress', methods=['POST'])
def update_challenge_progress(challenge_id):
    """Update challenge progress"""
    try:
        data = request.json
        
        result = gamification_service.update_challenge_progress(
            challenge_id=challenge_id,
            user_id=data.get('user_id'),
            progress=data.get('progress', 1)
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gamification_bp.route('/user/<user_id>/challenges/completed', methods=['GET'])
def get_completed_challenges(user_id):
    """Get user's completed challenges"""
    try:
        completed = gamification_service.get_completed_challenges(user_id)
        return jsonify({'challenges': completed})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Achievements ====================

@gamification_bp.route('/user/<user_id>/achievements', methods=['GET'])
def get_achievements(user_id):
    """Get user achievements summary"""
    try:
        achievements = gamification_service.get_achievements_summary(user_id)
        return jsonify(achievements)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gamification_bp.route('/user/<user_id>/progress-summary', methods=['GET'])
def get_progress_summary(user_id):
    """Get gamification progress summary"""
    try:
        summary = gamification_service.get_progress_summary(user_id)
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Leaderboards ====================

@gamification_bp.route('/leaderboard/xp', methods=['GET'])
def get_xp_leaderboard():
    """Get XP leaderboard"""
    try:
        limit = request.args.get('limit', 100, type=int)
        timeframe = request.args.get('timeframe', 'all')
        
        leaderboard = gamification_service.get_xp_leaderboard(limit, timeframe)
        return jsonify({'leaderboard': leaderboard})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gamification_bp.route('/leaderboard/streak', methods=['GET'])
def get_streak_leaderboard():
    """Get streak leaderboard"""
    try:
        limit = request.args.get('limit', 100, type=int)
        
        leaderboard = gamification_service.get_streak_leaderboard(limit)
        return jsonify({'leaderboard': leaderboard})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
