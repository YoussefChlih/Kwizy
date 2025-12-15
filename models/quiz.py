"""
Quiz Models
"""

from models.database import db, TimestampMixin
import uuid
from datetime import datetime


class Quiz(db.Model, TimestampMixin):
    """Quiz model"""
    __tablename__ = 'quizzes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    
    # Configuration
    difficulty = db.Column(db.String(20), default='moyen')
    question_types = db.Column(db.JSON)  # List of question types
    num_questions = db.Column(db.Integer)
    time_limit_minutes = db.Column(db.Integer)
    
    # Learning mode
    mode = db.Column(db.String(20), default='practice')  # practice, exam, discovery, quick
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    is_public = db.Column(db.Boolean, default=False)
    
    # Owner
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(36))  # For anonymous users
    
    # Language
    language = db.Column(db.String(10), default='fr')
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('Document', secondary='quiz_documents', back_populates='quizzes')
    
    # Cache for generated quiz
    cached_data = db.Column(db.JSON)
    cache_expires_at = db.Column(db.DateTime)
    
    def to_dict(self, include_questions=False):
        result = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'difficulty': self.difficulty,
            'question_types': self.question_types,
            'num_questions': self.num_questions,
            'time_limit_minutes': self.time_limit_minutes,
            'mode': self.mode,
            'status': self.status,
            'is_public': self.is_public,
            'language': self.language,
            'document_count': len(self.documents),
            'attempt_count': self.attempts.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_questions:
            result['questions'] = [q.to_dict() for q in self.questions]
        
        return result


class Question(db.Model, TimestampMixin):
    """Question model"""
    __tablename__ = 'questions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = db.Column(db.String(36), db.ForeignKey('quizzes.id'), nullable=False)
    
    # Content
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(30), nullable=False)  # qcm, vrai_faux, comprehension, etc.
    difficulty = db.Column(db.String(20), default='moyen')
    
    # Options (for QCM)
    options = db.Column(db.JSON)  # List of options
    correct_answer = db.Column(db.Text)
    explanation = db.Column(db.Text)
    
    # Source reference
    source_document_id = db.Column(db.String(36), db.ForeignKey('documents.id'), nullable=True)
    source_page = db.Column(db.Integer)
    source_text = db.Column(db.Text)  # The text chunk the question was generated from
    
    # Question order
    order_index = db.Column(db.Integer, default=0)
    
    # Quality metrics
    quality_score = db.Column(db.Float)  # Auto-assessed quality
    is_flagged = db.Column(db.Boolean, default=False)  # User-flagged as problematic
    flag_reason = db.Column(db.String(500))
    
    # Keywords for semantic matching
    keywords = db.Column(db.JSON)
    
    # Relationships
    answers = db.relationship('UserAnswer', backref='question', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'question': self.question_text,
            'type': self.question_type,
            'difficulty': self.difficulty,
            'options': self.options,
            'correct_answer': self.correct_answer,
            'explanation': self.explanation,
            'source_document_id': self.source_document_id,
            'source_page': self.source_page,
            'order_index': self.order_index,
            'quality_score': self.quality_score,
            'is_flagged': self.is_flagged,
            'keywords': self.keywords
        }


class QuizAttempt(db.Model, TimestampMixin):
    """Quiz attempt/session model"""
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = db.Column(db.String(36), db.ForeignKey('quizzes.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(36))
    
    # Status
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed, abandoned
    
    # Timing
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    time_spent_seconds = db.Column(db.Integer)
    
    # Results
    score = db.Column(db.Float)
    correct_count = db.Column(db.Integer)
    total_questions = db.Column(db.Integer)
    
    # Progress (for resumable quizzes)
    current_question_index = db.Column(db.Integer, default=0)
    answers_snapshot = db.Column(db.JSON)  # Saved answers for resume
    
    # Learning mode used
    mode = db.Column(db.String(20))
    
    # Relationships
    answers = db.relationship('UserAnswer', backref='attempt', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'user_id': self.user_id,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'time_spent_seconds': self.time_spent_seconds,
            'score': self.score,
            'correct_count': self.correct_count,
            'total_questions': self.total_questions,
            'current_question_index': self.current_question_index,
            'mode': self.mode
        }


class UserAnswer(db.Model, TimestampMixin):
    """User's answer to a question"""
    __tablename__ = 'user_answers'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    attempt_id = db.Column(db.String(36), db.ForeignKey('quiz_attempts.id'), nullable=False)
    question_id = db.Column(db.String(36), db.ForeignKey('questions.id'), nullable=False)
    
    # Answer
    answer_text = db.Column(db.Text)
    answer_option = db.Column(db.String(10))  # For QCM: A, B, C, D
    
    # Evaluation
    is_correct = db.Column(db.Boolean)
    partial_score = db.Column(db.Float)  # For partial credit
    confidence_score = db.Column(db.Float)  # For open questions
    
    # Timing
    time_spent_seconds = db.Column(db.Integer)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Feedback
    feedback = db.Column(db.Text)  # AI-generated feedback
    
    def to_dict(self):
        return {
            'id': self.id,
            'attempt_id': self.attempt_id,
            'question_id': self.question_id,
            'answer_text': self.answer_text,
            'answer_option': self.answer_option,
            'is_correct': self.is_correct,
            'partial_score': self.partial_score,
            'confidence_score': self.confidence_score,
            'time_spent_seconds': self.time_spent_seconds,
            'feedback': self.feedback
        }
