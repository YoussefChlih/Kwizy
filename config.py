import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB max
    
    # Database settings
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///quiz_app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Supabase settings
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    USE_SUPABASE = os.getenv('USE_SUPABASE', 'true').lower() == 'true'
    
    # Allowed file extensions (enhanced)
    ALLOWED_EXTENSIONS = {'pdf', 'pptx', 'ppt', 'docx', 'doc', 'txt', 'rtf', 'png', 'jpg', 'jpeg'}
    
    # RAG settings - augmenté pour mieux capturer le contenu
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 100
    TOP_K_RESULTS = 10
    
    # Vector Store settings
    USE_CHROMADB = os.getenv('USE_CHROMADB', 'true').lower() == 'true'
    CHROMADB_PERSIST_DIR = os.getenv('CHROMADB_PERSIST_DIR', './chroma_db')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    
    # Quiz settings
    DIFFICULTY_LEVELS = {
        'facile': 'easy',
        'moyen': 'medium', 
        'difficile': 'hard'
    }
    
    QUESTION_TYPES = {
        'comprehension': 'comprehension',
        'memorisation': 'memorization',
        'qcm': 'multiple_choice',
        'vrai_faux': 'true_false',
        'reponse_courte': 'short_answer'
    }
    
    # Gamification settings
    XP_MULTIPLIERS = {
        'quiz_complete': 10,
        'correct_answer': 5,
        'perfect_score': 50,
        'streak_bonus': 2,
        'daily_challenge': 25,
        'flashcard_review': 2
    }
    
    BADGE_DEFINITIONS = {
        'first_quiz': {'name': 'Premier Quiz', 'description': 'Compléter votre premier quiz', 'icon': '[BADGE]'},
        'perfect_score': {'name': 'Score Parfait', 'description': 'Obtenir 100% sur un quiz', 'icon': '[STAR]'},
        'streak_7': {'name': 'Série de 7 jours', 'description': 'Étudier 7 jours consécutifs', 'icon': '[FIRE]'},
        'streak_30': {'name': 'Série de 30 jours', 'description': 'Étudier 30 jours consécutifs', 'icon': '[DIAMOND]'},
        'quiz_master': {'name': 'Maître du Quiz', 'description': 'Compléter 100 quiz', 'icon': '[CROWN]'},
        'social_butterfly': {'name': 'Papillon Social', 'description': 'Partager 10 quiz', 'icon': '[BUTTERFLY]'},
        'community_star': {'name': 'Étoile Communautaire', 'description': 'Avoir un quiz avec 50+ évaluations', 'icon': '[STAR]'}
    }
    
    # Spaced Repetition settings (SM-2 algorithm)
    SM2_INITIAL_EASE = 2.5
    SM2_MIN_EASE = 1.3
    SM2_EASE_BONUS = 0.1
    SM2_EASY_INTERVAL_MODIFIER = 1.3
    
    # WebSocket settings
    SOCKETIO_MESSAGE_QUEUE = os.getenv('SOCKETIO_MESSAGE_QUEUE', None)
    
    # OCR settings (optional)
    TESSERACT_CMD = os.getenv('TESSERACT_CMD', None)
    
    # Language settings
    SUPPORTED_LANGUAGES = ['fr', 'en', 'es', 'de', 'ar']
    DEFAULT_LANGUAGE = 'fr'
