"""
User Model
"""

from models.database import db, TimestampMixin
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


class User(db.Model, TimestampMixin):
    """User model for authentication and profile"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    display_name = db.Column(db.String(100))
    avatar_url = db.Column(db.String(500))
    preferred_language = db.Column(db.String(10), default='fr')
    
    # Accessibility settings
    font_size = db.Column(db.String(20), default='medium')
    dyslexia_mode = db.Column(db.Boolean, default=False)
    dark_mode = db.Column(db.Boolean, default=True)
    theme = db.Column(db.String(20), default='dark')  # dark, light, auto
    high_contrast = db.Column(db.Boolean, default=False)
    
    # User preferences
    profile_type = db.Column(db.String(20), default='student')  # student, teacher, learning_disabled
    notification_mode = db.Column(db.String(20), default='all')  # all, email_only, none
    study_mode = db.Column(db.String(20), default='balanced')  # intense, balanced, relaxed
    
    # Role
    role = db.Column(db.String(20), default='student')  # student, teacher, admin
    
    # Teacher-specific
    class_id = db.Column(db.String(36), db.ForeignKey('classes.id'), nullable=True)
    
    # Relationships
    documents = db.relationship('Document', backref='owner', lazy='dynamic')
    quizzes = db.relationship('Quiz', backref='creator', lazy='dynamic')
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy='dynamic')
    flashcard_reviews = db.relationship('FlashcardReview', backref='user', lazy='dynamic')
    stats = db.relationship('UserStats', backref='user', uselist=False)
    badges = db.relationship('UserBadge', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name,
            'avatar_url': self.avatar_url,
            'preferred_language': self.preferred_language,
            'role': self.role,
            'profile_type': self.profile_type,
            'settings': {
                'font_size': self.font_size,
                'dyslexia_mode': self.dyslexia_mode,
                'dark_mode': self.dark_mode,
                'theme': self.theme,
                'high_contrast': self.high_contrast,
                'notification_mode': self.notification_mode,
                'study_mode': self.study_mode
            },
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Class(db.Model, TimestampMixin):
    """Class model for teacher-student relationships"""
    __tablename__ = 'classes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.String(36), nullable=False)
    join_code = db.Column(db.String(20), unique=True)
    
    # Relationships
    students = db.relationship('User', backref='enrolled_class', lazy='dynamic')
    assigned_quizzes = db.relationship('ClassQuizAssignment', backref='class_', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'teacher_id': self.teacher_id,
            'join_code': self.join_code,
            'student_count': self.students.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ClassQuizAssignment(db.Model, TimestampMixin):
    """Assignment of quizzes to classes"""
    __tablename__ = 'class_quiz_assignments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    class_id = db.Column(db.String(36), db.ForeignKey('classes.id'), nullable=False)
    quiz_id = db.Column(db.String(36), db.ForeignKey('quizzes.id'), nullable=False)
    due_date = db.Column(db.DateTime)
    max_attempts = db.Column(db.Integer, default=1)
    time_limit_minutes = db.Column(db.Integer)
    
    def to_dict(self):
        return {
            'id': self.id,
            'class_id': self.class_id,
            'quiz_id': self.quiz_id,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'max_attempts': self.max_attempts,
            'time_limit_minutes': self.time_limit_minutes
        }
