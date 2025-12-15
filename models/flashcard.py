"""
Flashcard Models for Spaced Repetition System
Implements SM-2 Algorithm
"""

from models.database import db, TimestampMixin
import uuid
from datetime import datetime, timedelta


class Flashcard(db.Model, TimestampMixin):
    """Flashcard for spaced repetition"""
    __tablename__ = 'flashcards'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Content
    front = db.Column(db.Text, nullable=False)  # Question
    back = db.Column(db.Text, nullable=False)   # Answer
    hint = db.Column(db.Text)
    
    # Source
    question_id = db.Column(db.String(36), db.ForeignKey('questions.id'), nullable=True)
    document_id = db.Column(db.String(36), db.ForeignKey('documents.id'), nullable=True)
    
    # Owner
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(36))
    
    # Tags and categories
    tags = db.Column(db.JSON)
    category = db.Column(db.String(100))
    
    # Relationships
    reviews = db.relationship('FlashcardReview', backref='flashcard', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'front': self.front,
            'back': self.back,
            'hint': self.hint,
            'question_id': self.question_id,
            'document_id': self.document_id,
            'tags': self.tags,
            'category': self.category,
            'review_count': self.reviews.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class FlashcardReview(db.Model, TimestampMixin):
    """Review tracking for SM-2 algorithm"""
    __tablename__ = 'flashcard_reviews'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    flashcard_id = db.Column(db.String(36), db.ForeignKey('flashcards.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(36))
    
    # SM-2 Algorithm Parameters
    easiness_factor = db.Column(db.Float, default=2.5)  # EF (minimum 1.3)
    interval = db.Column(db.Integer, default=1)  # Days until next review
    repetitions = db.Column(db.Integer, default=0)  # Number of successful reviews
    
    # Review data
    quality = db.Column(db.Integer)  # 0-5 rating from user
    reviewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    next_review = db.Column(db.DateTime)
    
    # Response time
    response_time_ms = db.Column(db.Integer)
    
    def calculate_next_review(self, quality):
        """
        Implement SM-2 algorithm
        Quality: 0-5 (0-2: incorrect, 3-5: correct with varying difficulty)
        """
        # Update easiness factor
        self.easiness_factor = max(1.3, self.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        
        if quality < 3:
            # Reset repetitions for incorrect answers
            self.repetitions = 0
            self.interval = 1
        else:
            if self.repetitions == 0:
                self.interval = 1
            elif self.repetitions == 1:
                self.interval = 6
            else:
                self.interval = round(self.interval * self.easiness_factor)
            
            self.repetitions += 1
        
        self.quality = quality
        self.reviewed_at = datetime.utcnow()
        self.next_review = datetime.utcnow() + timedelta(days=self.interval)
        
        return self.next_review
    
    def to_dict(self):
        return {
            'id': self.id,
            'flashcard_id': self.flashcard_id,
            'easiness_factor': self.easiness_factor,
            'interval': self.interval,
            'repetitions': self.repetitions,
            'quality': self.quality,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'next_review': self.next_review.isoformat() if self.next_review else None
        }


class FlashcardDeck(db.Model, TimestampMixin):
    """Collection of flashcards"""
    __tablename__ = 'flashcard_decks'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Owner
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    
    # Settings
    cards_per_session = db.Column(db.Integer, default=20)
    new_cards_per_day = db.Column(db.Integer, default=10)
    
    # Relationships
    cards = db.relationship('Flashcard', secondary='deck_flashcards', backref='decks')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'cards_per_session': self.cards_per_session,
            'new_cards_per_day': self.new_cards_per_day,
            'card_count': len(self.cards),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Association table for deck-flashcard relationship
deck_flashcards = db.Table('deck_flashcards',
    db.Column('deck_id', db.String(36), db.ForeignKey('flashcard_decks.id'), primary_key=True),
    db.Column('flashcard_id', db.String(36), db.ForeignKey('flashcards.id'), primary_key=True)
)
