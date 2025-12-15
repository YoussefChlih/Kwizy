"""
Database Models for Quiz RAG System
"""

from models.database import db, init_db
from models.user import User
from models.document import Document, DocumentChunk
from models.quiz import Quiz, Question, QuizAttempt, UserAnswer
from models.flashcard import Flashcard, FlashcardReview
from models.collaboration import SharedQuiz, QuizRoom, LeaderboardEntry
from models.gamification import UserStats, Badge, UserBadge, Achievement, DailyChallenge
from models.community import PublicQuiz, QuizComment, QuizRating

__all__ = [
    'db', 'init_db',
    'User', 'Document', 'DocumentChunk',
    'Quiz', 'Question', 'QuizAttempt', 'UserAnswer',
    'Flashcard', 'FlashcardReview',
    'SharedQuiz', 'QuizRoom', 'LeaderboardEntry',
    'UserStats', 'Badge', 'UserBadge', 'Achievement', 'DailyChallenge',
    'PublicQuiz', 'QuizComment', 'QuizRating'
]
