"""
Document Routes - API endpoints for document processing
"""

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from services import DocumentService

document_bp = Blueprint('documents', __name__)
document_service = DocumentService()

ALLOWED_EXTENSIONS = {'pdf', 'pptx', 'docx', 'txt', 'rtf', 'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@document_bp.route('/upload', methods=['POST'])
def upload_document():
    """Upload and process a document"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        filename = secure_filename(file.filename)
        upload_path = os.path.join('uploads', filename)
        file.save(upload_path)
        
        user_id = request.form.get('user_id')
        
        result = document_service.process_document(
            file_path=upload_path,
            user_id=user_id
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/upload-multiple', methods=['POST'])
def upload_multiple_documents():
    """Upload and process multiple documents"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        user_id = request.form.get('user_id')
        
        results = []
        for file in files:
            if file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_path = os.path.join('uploads', filename)
                file.save(upload_path)
                
                result = document_service.process_document(
                    file_path=upload_path,
                    user_id=user_id
                )
                results.append(result)
        
        return jsonify({'documents': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/from-url', methods=['POST'])
def process_from_url():
    """Process content from a URL"""
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL required'}), 400
        
        result = document_service.process_from_url(
            url=url,
            user_id=data.get('user_id')
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/from-youtube', methods=['POST'])
def process_from_youtube():
    """Process content from YouTube video"""
    try:
        data = request.json
        video_url = data.get('video_url')
        
        if not video_url:
            return jsonify({'error': 'YouTube URL required'}), 400
        
        result = document_service.process_youtube_video(
            video_url=video_url,
            user_id=data.get('user_id')
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/user/<user_id>', methods=['GET'])
def get_user_documents(user_id):
    """Get all documents for a user"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        documents = document_service.get_user_documents(user_id, page, per_page)
        return jsonify(documents)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get a document by ID"""
    try:
        document = document_service.get_document(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        return jsonify(document)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/<document_id>/chunks', methods=['GET'])
def get_document_chunks(document_id):
    """Get document chunks"""
    try:
        chunks = document_service.get_document_chunks(document_id)
        return jsonify({'chunks': chunks})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/<document_id>/concepts', methods=['GET'])
def get_document_concepts(document_id):
    """Get extracted concepts from document"""
    try:
        concepts = document_service.extract_concepts(document_id)
        return jsonify({'concepts': concepts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a document"""
    try:
        result = document_service.delete_document(document_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/search', methods=['POST'])
def search_documents():
    """Search documents using RAG"""
    try:
        data = request.json
        
        results = document_service.search_documents(
            query=data.get('query', ''),
            user_id=data.get('user_id'),
            document_ids=data.get('document_ids'),
            top_k=data.get('top_k', 5)
        )
        
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@document_bp.route('/combine', methods=['POST'])
def combine_documents():
    """Combine multiple documents for quiz generation"""
    try:
        data = request.json
        document_ids = data.get('document_ids', [])
        
        if not document_ids:
            return jsonify({'error': 'Document IDs required'}), 400
        
        result = document_service.combine_documents(document_ids)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
