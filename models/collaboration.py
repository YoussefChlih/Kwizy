"""
Collaboration Models
Real-time quiz rooms, shared quizzes, leaderboards
"""

from models.database import db, TimestampMixin
import uuid
from datetime import datetime
import secrets


class SharedQuiz(db.Model, TimestampMixin):
    """Shareable quiz link"""
    __tablename__ = 'shared_quizzes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = db.Column(db.String(36), db.ForeignKey('quizzes.id'), nullable=False)
    
    # Share settings
    share_code = db.Column(db.String(20), unique=True, default=lambda: secrets.token_urlsafe(10))
    share_url = db.Column(db.String(500))
    
    # Access control
    password_protected = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(256))
    max_attempts = db.Column(db.Integer)
    expires_at = db.Column(db.DateTime)
    
    # Settings
    allow_review = db.Column(db.Boolean, default=True)  # Allow viewing correct answers after
    show_leaderboard = db.Column(db.Boolean, default=True)
    randomize_questions = db.Column(db.Boolean, default=False)
    
    # Stats
    view_count = db.Column(db.Integer, default=0)
    attempt_count = db.Column(db.Integer, default=0)
    
    # Creator
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'share_code': self.share_code,
            'share_url': self.share_url,
            'password_protected': self.password_protected,
            'max_attempts': self.max_attempts,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'allow_review': self.allow_review,
            'show_leaderboard': self.show_leaderboard,
            'randomize_questions': self.randomize_questions,
            'view_count': self.view_count,
            'attempt_count': self.attempt_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class QuizRoom(db.Model, TimestampMixin):
    """Real-time quiz room for competitions"""
    __tablename__ = 'quiz_rooms'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = db.Column(db.String(36), db.ForeignKey('quizzes.id'), nullable=False)
    
    # Room settings
    room_code = db.Column(db.String(10), unique=True, default=lambda: secrets.token_urlsafe(5).upper()[:6])
    name = db.Column(db.String(200))
    
    # Status
    status = db.Column(db.String(20), default='waiting')  # waiting, in_progress, completed
    
    # Timing
    scheduled_start = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    ended_at = db.Column(db.DateTime)
    question_time_limit = db.Column(db.Integer, default=30)  # Seconds per question
    
    # Settings
    max_participants = db.Column(db.Integer, default=50)
    show_live_scores = db.Column(db.Boolean, default=True)
    
    # Host
    host_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    
    # Current state
    current_question_index = db.Column(db.Integer, default=0)
    
    # Relationships
    participants = db.relationship('RoomParticipant', backref='room', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'room_code': self.room_code,
            'name': self.name,
            'status': self.status,
            'scheduled_start': self.scheduled_start.isoformat() if self.scheduled_start else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'question_time_limit': self.question_time_limit,
            'max_participants': self.max_participants,
            'show_live_scores': self.show_live_scores,
            'current_question_index': self.current_question_index,
            'participant_count': self.participants.count()
        }


class RoomParticipant(db.Model, TimestampMixin):
    """Participant in a quiz room"""
    __tablename__ = 'room_participants'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    room_id = db.Column(db.String(36), db.ForeignKey('quiz_rooms.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    
    # Anonymous participant info
    nickname = db.Column(db.String(50))
    avatar_emoji = db.Column(db.String(10))
    
    # Status
    status = db.Column(db.String(20), default='joined')  # joined, playing, finished, disconnected
    
    # Score
    score = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    streak = db.Column(db.Integer, default=0)  # Current correct answer streak
    
    # Timing
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'user_id': self.user_id,
            'nickname': self.nickname,
            'avatar_emoji': self.avatar_emoji,
            'status': self.status,
            'score': self.score,
            'correct_answers': self.correct_answers,
            'streak': self.streak
        }


class LeaderboardEntry(db.Model, TimestampMixin):
    """Global and quiz-specific leaderboard entries"""
    __tablename__ = 'leaderboard_entries'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Scope
    leaderboard_type = db.Column(db.String(20), default='global')  # global, quiz, weekly, daily
    quiz_id = db.Column(db.String(36), db.ForeignKey('quizzes.id'), nullable=True)
    
    # User
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    nickname = db.Column(db.String(50))  # For anonymous users
    
    # Score
    score = db.Column(db.Integer, nullable=False)
    rank = db.Column(db.Integer)
    
    # Stats
    quizzes_completed = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    average_time_seconds = db.Column(db.Float)
    
    # Time period
    period_start = db.Column(db.DateTime)
    period_end = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'leaderboard_type': self.leaderboard_type,
            'user_id': self.user_id,
            'nickname': self.nickname,
            'score': self.score,
            'rank': self.rank,
            'quizzes_completed': self.quizzes_completed,
            'correct_answers': self.correct_answers,
            'total_questions': self.total_questions,
            'average_time_seconds': self.average_time_seconds
        }
