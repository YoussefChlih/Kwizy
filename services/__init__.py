"""
Services Module
Business logic and service layer
"""

from services.quiz_service import QuizService
from services.document_service import DocumentService
from services.analytics_service import AnalyticsService
from services.flashcard_service import FlashcardService
from services.gamification_service import GamificationService
from services.collaboration_service import CollaborationService
from services.community_service import CommunityService
from services.user_service import UserService

# Try to import Supabase service
try:
    from services.supabase_service import SupabaseService, supabase_service
except ImportError:
    SupabaseService = None
    supabase_service = None

__all__ = [
    'QuizService',
    'DocumentService', 
    'AnalyticsService',
    'FlashcardService',
    'GamificationService',
    'CollaborationService',
    'CommunityService',
    'UserService',
    'SupabaseService',
    'supabase_service'
]
