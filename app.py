"""
Quiz RAG System - Flask Application
Main application file with routes and API endpoints
Enhanced with: Database, WebSocket, Multi-document support, Gamification, etc.
"""

import os
import uuid
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from config import Config
from document_processor import DocumentProcessor, get_file_info
from rag_system import RAGSystem
from quiz_generator import QuizGenerator

# Import new modules
try:
    from models import db, init_db
    from routes import register_blueprints
    DB_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Models/Routes import failed: {e}")
    DB_AVAILABLE = False

try:
    from flask_socketio import SocketIO
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False

# Import authentication components
try:
    from auth_routes import auth_bp
    AUTH_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Auth routes import failed: {e}")
    AUTH_AVAILABLE = False


# Initialize Flask app (API only - React frontend on separate port)
app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = Config.DATABASE_URL if hasattr(Config, 'DATABASE_URL') else 'sqlite:///quiz_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 7 * 24 * 60 * 60  # 7 days

# Configure CORS for both local development and production
is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('VERCEL') == '1'
if is_production:
    # In production (Vercel), allow all origins with credentials
    cors_origins = ['*']
else:
    # In development, allow specific localhost origins
    cors_origins = ['http://localhost:3000', 'http://localhost:5000', 'http://127.0.0.1:3000', 'http://127.0.0.1:5000']

# Enable CORS for React frontend
CORS(app, origins=cors_origins, supports_credentials=not is_production)

# Initialize SocketIO if available
socketio = None
if SOCKETIO_AVAILABLE:
    socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize database if available
if DB_AVAILABLE:
    try:
        init_db(app)
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        DB_AVAILABLE = False

# Register API blueprints if available
if DB_AVAILABLE:
    try:
        register_blueprints(app)
        logger.info("API routes registered")
    except Exception as e:
        logger.error(f"Routes registration failed: {e}")

# Register authentication blueprint
if AUTH_AVAILABLE:
    try:
        app.register_blueprint(auth_bp)
        logger.info("Authentication routes registered")
    except Exception as e:
        logger.error(f"Auth routes registration failed: {e}")

# Ensure upload folder exists
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
except Exception as e:
    logger.warning(f"Could not create upload folder: {e}")

# Initialize components with error handling
try:
    document_processor = DocumentProcessor()
    logger.info("Document processor initialized")
except Exception as e:
    logger.error(f"Document processor initialization failed: {e}")
    document_processor = None

try:
    rag_system = RAGSystem(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP
    )
    logger.info("RAG system initialized")
except Exception as e:
    logger.error(f"RAG system initialization failed: {e}")
    rag_system = None

# Quiz generator (initialized lazily when API key is available)
quiz_generator = None


def get_quiz_generator():
    """Get or create quiz generator instance"""
    global quiz_generator
    if quiz_generator is None:
        api_key = Config.MISTRAL_API_KEY
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not configured")
        quiz_generator = QuizGenerator(api_key)
    return quiz_generator


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


# ==================== API Routes Only ====================
# No web routes - React frontend runs on localhost:3000
# Backend API only on localhost:5000

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with detailed status"""
    return jsonify({
        'status': 'healthy',
        'message': 'Quiz RAG System is running',
        'components': {
            'document_processor': 'ok' if document_processor else 'unavailable',
            'rag_system': 'ok' if rag_system else 'unavailable',
            'database': 'ok' if DB_AVAILABLE else 'unavailable',
            'socketio': 'ok' if SOCKETIO_AVAILABLE else 'unavailable',
            'authentication': 'ok' if AUTH_AVAILABLE else 'unavailable'
        }
    })


@app.route('/api/options', methods=['GET'])
def get_options():
    """Get available quiz options (difficulties and question types)"""
    try:
        generator = get_quiz_generator()
        options = generator.get_available_options()
        return jsonify({
            'success': True,
            'data': options
        })
    except ValueError as e:
        # Return default options if API key not set
        return jsonify({
            'success': True,
            'data': {
                'difficulties': [
                    {'key': 'facile', 'name': 'Facile', 'description': 'Questions simples'},
                    {'key': 'moyen', 'name': 'Moyen', 'description': 'Questions modérées'},
                    {'key': 'difficile', 'name': 'Difficile', 'description': 'Questions complexes'}
                ],
                'question_types': [
                    {'key': 'comprehension', 'name': 'Compréhension', 'description': 'Compréhension du contenu'},
                    {'key': 'memorisation', 'name': 'Mémorisation', 'description': 'Rappel de faits'},
                    {'key': 'qcm', 'name': 'QCM', 'description': 'Choix multiples'},
                    {'key': 'vrai_faux', 'name': 'Vrai/Faux', 'description': 'Questions vrai/faux'},
                    {'key': 'reponse_courte', 'name': 'Réponse Courte', 'description': 'Réponses brèves'}
                ]
            }
        })


@app.route('/api/upload', methods=['POST'])
def upload_document():
    """Upload and process a document"""
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file provided'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'No file selected'
        }), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': f'File type not allowed. Supported types: {", ".join(Config.ALLOWED_EXTENSIONS)}'
        }), 400
    
    try:
        # Save the file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Process the document
        text_content = document_processor.process(file_path)
        
        if not text_content or not text_content.strip():
            os.remove(file_path)
            return jsonify({
                'success': False,
                'error': 'Could not extract text from document'
            }), 400
        
        # Add to RAG system
        num_chunks = rag_system.add_document(text_content, unique_filename)
        
        # Get file info
        file_info = get_file_info(file_path)
        
        return jsonify({
            'success': True,
            'message': 'Document processed successfully',
            'data': {
                'filename': filename,
                'file_id': unique_filename,
                'text_length': len(text_content),
                'chunks_created': num_chunks,
                'file_size': file_info['size'] if file_info else 0
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Get information about loaded documents"""
    stats = rag_system.get_stats()
    return jsonify({
        'success': True,
        'data': stats
    })


@app.route('/api/documents/clear', methods=['POST'])
def clear_documents():
    """Clear all loaded documents"""
    try:
        rag_system.clear()
        
        # Optionally clear upload folder
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        return jsonify({
            'success': True,
            'message': 'All documents cleared'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate-quiz', methods=['POST'])
def generate_quiz():
    """Generate a quiz from uploaded documents"""
    try:
        # Check if documents are loaded
        stats = rag_system.get_stats()
        if stats['total_chunks'] == 0:
            return jsonify({
                'success': False,
                'error': 'No documents loaded. Please upload a document first.'
            }), 400
        
        # Get parameters from request
        data = request.get_json() or {}
        
        num_questions = data.get('num_questions', 5)
        difficulty = data.get('difficulty', 'moyen')
        question_types = data.get('question_types', ['qcm'])
        topic = data.get('topic', '')  # Optional topic focus
        
        # Validate parameters
        num_questions = min(max(1, int(num_questions)), 20)  # Between 1 and 20
        
        if isinstance(question_types, str):
            question_types = [question_types]
        
        # Get relevant context
        if topic:
            context = rag_system.get_relevant_context(topic, top_k=Config.TOP_K_RESULTS)
        else:
            context = rag_system.get_full_context()
        
        # Generate quiz
        generator = get_quiz_generator()
        quiz = generator.generate_quiz(
            context=context,
            num_questions=num_questions,
            difficulty=difficulty,
            question_types=question_types
        )
        
        return jsonify({
            'success': quiz.get('success', False),
            'data': quiz
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error generating quiz: {str(e)}'
        }), 500


@app.route('/api/search', methods=['POST'])
def search_documents():
    """Search through loaded documents"""
    try:
        data = request.get_json() or {}
        query = data.get('query', '')
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        results = rag_system.vector_store.search(query, top_k)
        
        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'results': results
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 16MB.'
    }), 413


# ==================== Main ====================

if __name__ == '__main__':
    print("=" * 50)
    print("Quiz RAG System - Enhanced Version")
    print("=" * 50)
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"Allowed extensions: {Config.ALLOWED_EXTENSIONS}")
    print(f"Database: {' Available' if DB_AVAILABLE else ' Not available'}")
    print(f"WebSocket: {' Available' if SOCKETIO_AVAILABLE else ' Not available'}")
    print("=" * 50)
    print("\nAvailable endpoints:")
    print("  - Main app: http://localhost:5000")
    print("  - API docs: http://localhost:5000/api/health")
    print("\nNew API routes (when DB is available):")
    print("  - /api/user/* - User management")
    print("  - /api/quiz/* - Quiz operations")
    print("  - /api/documents/* - Document handling")
    print("  - /api/flashcards/* - Spaced repetition")
    print("  - /api/collaboration/* - Real-time rooms")
    print("  - /api/analytics/* - Statistics")
    print("  - /api/gamification/* - Badges & challenges")
    print("  - /api/community/* - Public library")
    print("=" * 50)
    
    # Production vs Development settings
    is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('VERCEL') == '1'
    debug_mode = not is_production
    
    if SOCKETIO_AVAILABLE and socketio:
        socketio.run(app, debug=debug_mode, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
    else:
        app.run(debug=debug_mode, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
