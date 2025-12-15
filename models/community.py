"""
Community Models
Public quiz library, ratings, comments, tags
"""

from models.database import db, TimestampMixin
import uuid
from datetime import datetime


class PublicQuiz(db.Model, TimestampMixin):
    """Public quiz in the community library"""
    __tablename__ = 'public_quizzes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = db.Column(db.String(36), db.ForeignKey('quizzes.id'), nullable=False)
    
    # Publisher info
    published_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Moderation
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, flagged
    moderated_by = db.Column(db.String(36))
    moderated_at = db.Column(db.DateTime)
    
    # Metadata
    title = db.Column(db.String(500))
    description = db.Column(db.Text)
    thumbnail_url = db.Column(db.String(500))
    
    # Categorization
    category = db.Column(db.String(100))
    tags = db.Column(db.JSON)  # List of tags
    language = db.Column(db.String(10), default='fr')
    
    # Stats
    view_count = db.Column(db.Integer, default=0)
    play_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    share_count = db.Column(db.Integer, default=0)
    
    # Ratings
    average_rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    
    # Featured/Promoted
    is_featured = db.Column(db.Boolean, default=False)
    featured_until = db.Column(db.DateTime)
    
    # Relationships
    ratings = db.relationship('QuizRating', backref='public_quiz', lazy='dynamic')
    comments = db.relationship('QuizComment', backref='public_quiz', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'published_by': self.published_by,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'status': self.status,
            'title': self.title,
            'description': self.description,
            'thumbnail_url': self.thumbnail_url,
            'category': self.category,
            'tags': self.tags,
            'language': self.language,
            'view_count': self.view_count,
            'play_count': self.play_count,
            'like_count': self.like_count,
            'average_rating': self.average_rating,
            'rating_count': self.rating_count,
            'is_featured': self.is_featured
        }


class QuizRating(db.Model, TimestampMixin):
    """User rating for a public quiz"""
    __tablename__ = 'quiz_ratings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    public_quiz_id = db.Column(db.String(36), db.ForeignKey('public_quizzes.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(36))
    
    # Rating (1-5 stars)
    rating = db.Column(db.Integer, nullable=False)
    
    # Unique constraint: one rating per user per quiz
    __table_args__ = (
        db.UniqueConstraint('public_quiz_id', 'user_id', name='unique_user_quiz_rating'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'public_quiz_id': self.public_quiz_id,
            'rating': self.rating,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class QuizComment(db.Model, TimestampMixin):
    """User comment on a public quiz"""
    __tablename__ = 'quiz_comments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    public_quiz_id = db.Column(db.String(36), db.ForeignKey('public_quizzes.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    
    # Content
    content = db.Column(db.Text, nullable=False)
    
    # Reply to another comment
    parent_id = db.Column(db.String(36), db.ForeignKey('quiz_comments.id'), nullable=True)
    
    # Moderation
    is_flagged = db.Column(db.Boolean, default=False)
    is_hidden = db.Column(db.Boolean, default=False)
    
    # Likes
    like_count = db.Column(db.Integer, default=0)
    
    # Relationships
    replies = db.relationship('QuizComment', backref=db.backref('parent', remote_side=[id]))
    author = db.relationship('User', backref='comments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'public_quiz_id': self.public_quiz_id,
            'user_id': self.user_id,
            'author_name': self.author.display_name if self.author else 'Anonymous',
            'content': self.content,
            'parent_id': self.parent_id,
            'like_count': self.like_count,
            'reply_count': len(self.replies),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class QuizCategory(db.Model, TimestampMixin):
    """Quiz categories for organization"""
    __tablename__ = 'quiz_categories'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    color = db.Column(db.String(20))
    
    # Parent category for hierarchy
    parent_id = db.Column(db.String(36), db.ForeignKey('quiz_categories.id'), nullable=True)
    
    # Order
    display_order = db.Column(db.Integer, default=0)
    
    # Relationships
    subcategories = db.relationship('QuizCategory', backref=db.backref('parent', remote_side=[id]))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'parent_id': self.parent_id,
            'subcategories': [sub.to_dict() for sub in self.subcategories]
        }


class QuizReport(db.Model, TimestampMixin):
    """Report problematic quizzes or questions"""
    __tablename__ = 'quiz_reports'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # What's being reported
    quiz_id = db.Column(db.String(36), db.ForeignKey('quizzes.id'), nullable=True)
    question_id = db.Column(db.String(36), db.ForeignKey('questions.id'), nullable=True)
    comment_id = db.Column(db.String(36), db.ForeignKey('quiz_comments.id'), nullable=True)
    
    # Reporter
    reported_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    
    # Report details
    reason = db.Column(db.String(50), nullable=False)  # incorrect, inappropriate, bias, other
    description = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, reviewed, resolved, dismissed
    resolved_by = db.Column(db.String(36))
    resolved_at = db.Column(db.DateTime)
    resolution_notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'question_id': self.question_id,
            'comment_id': self.comment_id,
            'reason': self.reason,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
