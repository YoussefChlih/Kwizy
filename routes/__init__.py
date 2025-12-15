"""
Routes Module - API endpoints
"""

from routes.quiz_routes import quiz_bp
from routes.document_routes import document_bp
from routes.user_routes import user_bp
from routes.flashcard_routes import flashcard_bp
from routes.collaboration_routes import collaboration_bp
from routes.analytics_routes import analytics_bp
from routes.gamification_routes import gamification_bp
from routes.community_routes import community_bp

__all__ = [
    'quiz_bp',
    'document_bp',
    'user_bp',
    'flashcard_bp',
    'collaboration_bp',
    'analytics_bp',
    'gamification_bp',
    'community_bp'
]


def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(quiz_bp, url_prefix='/api/quiz')
    app.register_blueprint(document_bp, url_prefix='/api/documents')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(flashcard_bp, url_prefix='/api/flashcards')
    app.register_blueprint(collaboration_bp, url_prefix='/api/collaboration')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(gamification_bp, url_prefix='/api/gamification')
    app.register_blueprint(community_bp, url_prefix='/api/community')
