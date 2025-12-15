"""
Community Routes - API endpoints for public library, ratings, sharing
"""

from flask import Blueprint, request, jsonify
from services import CommunityService

community_bp = Blueprint('community', __name__)
community_service = CommunityService()


# ==================== Public Quiz Library ====================

@community_bp.route('/publish', methods=['POST'])
def publish_quiz():
    """Publish a quiz to the public library"""
    try:
        data = request.json
        
        result = community_service.publish_quiz(
            quiz_id=data.get('quiz_id'),
            user_id=data.get('user_id'),
            title=data.get('title'),
            description=data.get('description'),
            category=data.get('category'),
            tags=data.get('tags'),
            language=data.get('language', 'fr'),
            is_anonymous=data.get('is_anonymous', False)
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@community_bp.route('/search', methods=['GET'])
def search_quizzes():
    """Search public quiz library"""
    try:
        query = request.args.get('query')
        category = request.args.get('category')
        tags = request.args.getlist('tags')
        difficulty = request.args.get('difficulty')
        language = request.args.get('language')
        sort_by = request.args.get('sort_by', 'recent')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        results = community_service.search_public_quizzes(
            query=query,
            category=category,
            tags=tags if tags else None,
            difficulty=difficulty,
            language=language,
            sort_by=sort_by,
            page=page,
            per_page=per_page
        )
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@community_bp.route('/quiz/<public_quiz_id>', methods=['GET'])
def get_public_quiz(public_quiz_id):
    """Get a public quiz by ID"""
    try:
        quiz = community_service.get_public_quiz(public_quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        return jsonify(quiz)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@community_bp.route('/quiz/<public_quiz_id>/play', methods=['GET'])
def play_public_quiz(public_quiz_id):
    """Get quiz for playing"""
    try:
        result = community_service.play_public_quiz(public_quiz_id)
        if not result:
            return jsonify({'error': 'Quiz not found'}), 404
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Ratings ====================

@community_bp.route('/quiz/<public_quiz_id>/rate', methods=['POST'])
def rate_quiz(public_quiz_id):
    """Rate a public quiz"""
    try:
        data = request.json
        
        result = community_service.rate_quiz(
            public_quiz_id=public_quiz_id,
            user_id=data.get('user_id'),
            rating=data.get('rating'),
            review=data.get('review')
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@community_bp.route('/quiz/<public_quiz_id>/ratings', methods=['GET'])
def get_quiz_ratings(public_quiz_id):
    """Get ratings for a quiz"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        ratings = community_service.get_quiz_ratings(
            public_quiz_id=public_quiz_id,
            page=page,
            per_page=per_page
        )
        
        return jsonify(ratings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Comments ====================

@community_bp.route('/quiz/<public_quiz_id>/comment', methods=['POST'])
def add_comment(public_quiz_id):
    """Add a comment to a quiz"""
    try:
        data = request.json
        
        result = community_service.add_comment(
            public_quiz_id=public_quiz_id,
            user_id=data.get('user_id'),
            content=data.get('content'),
            parent_comment_id=data.get('parent_comment_id')
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@community_bp.route('/quiz/<public_quiz_id>/comments', methods=['GET'])
def get_quiz_comments(public_quiz_id):
    """Get comments for a quiz"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        comments = community_service.get_quiz_comments(
            public_quiz_id=public_quiz_id,
            page=page,
            per_page=per_page
        )
        
        return jsonify(comments)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@community_bp.route('/comment/<comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """Delete a comment"""
    try:
        user_id = request.args.get('user_id')
        
        result = community_service.delete_comment(comment_id, user_id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Tags & Categories ====================

@community_bp.route('/tags/popular', methods=['GET'])
def get_popular_tags():
    """Get popular tags"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        tags = community_service.get_popular_tags(limit)
        return jsonify({'tags': tags})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@community_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories with counts"""
    try:
        categories = community_service.get_categories()
        return jsonify({'categories': categories})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Featured & Trending ====================

@community_bp.route('/featured', methods=['GET'])
def get_featured_quizzes():
    """Get featured quizzes"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        featured = community_service.get_featured_quizzes(limit)
        return jsonify({'quizzes': featured})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@community_bp.route('/trending', methods=['GET'])
def get_trending_quizzes():
    """Get trending quizzes"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        trending = community_service.get_trending_quizzes(limit)
        return jsonify({'quizzes': trending})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@community_bp.route('/recommendations/<user_id>', methods=['GET'])
def get_recommendations(user_id):
    """Get personalized quiz recommendations"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        recommendations = community_service.get_recommended_for_user(user_id, limit)
        return jsonify({'quizzes': recommendations})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Reporting ====================

@community_bp.route('/quiz/<public_quiz_id>/report', methods=['POST'])
def report_quiz(public_quiz_id):
    """Report a quiz"""
    try:
        data = request.json
        
        result = community_service.report_quiz(
            public_quiz_id=public_quiz_id,
            user_id=data.get('user_id'),
            reason=data.get('reason'),
            details=data.get('details')
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
