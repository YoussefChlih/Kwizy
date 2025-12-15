"""
Quiz Routes - API endpoints for quiz management
"""

from flask import Blueprint, request, jsonify
from services import QuizService

quiz_bp = Blueprint('quiz', __name__)
quiz_service = QuizService()


@quiz_bp.route('/generate', methods=['POST'])
def generate_quiz():
    """Generate a new quiz from document content"""
    try:
        data = request.json
        
        result = quiz_service.generate_quiz(
            content=data.get('content', ''),
            num_questions=data.get('num_questions', 10),
            difficulty=data.get('difficulty', 'moyen'),
            question_types=data.get('question_types', ['qcm', 'vrai_faux']),
            topic=data.get('topic'),
            focus_concepts=data.get('focus_concepts'),
            user_id=data.get('user_id')
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@quiz_bp.route('/adaptive/generate', methods=['POST'])
def generate_adaptive_quiz():
    """Generate quiz with adaptive difficulty"""
    try:
        data = request.json
        
        result = quiz_service.generate_adaptive_quiz(
            content=data.get('content', ''),
            user_id=data.get('user_id'),
            num_questions=data.get('num_questions', 10),
            topic=data.get('topic')
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@quiz_bp.route('/<quiz_id>', methods=['GET'])
def get_quiz(quiz_id):
    """Get a quiz by ID"""
    try:
        quiz = quiz_service.get_quiz(quiz_id)
        if not quiz:
            return jsonify({'error': 'Quiz not found'}), 404
        return jsonify(quiz)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@quiz_bp.route('/<quiz_id>/submit', methods=['POST'])
def submit_quiz(quiz_id):
    """Submit quiz answers"""
    try:
        data = request.json
        
        result = quiz_service.submit_quiz(
            quiz_id=quiz_id,
            answers=data.get('answers', {}),
            user_id=data.get('user_id'),
            time_taken=data.get('time_taken')
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@quiz_bp.route('/<quiz_id>/follow-up', methods=['POST'])
def get_follow_up(quiz_id):
    """Get follow-up questions for wrong answers"""
    try:
        data = request.json
        
        result = quiz_service.generate_follow_up_questions(
            quiz_id=quiz_id,
            wrong_question_ids=data.get('wrong_question_ids', [])
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@quiz_bp.route('/user/<user_id>', methods=['GET'])
def get_user_quizzes(user_id):
    """Get all quizzes for a user"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        quizzes = quiz_service.get_user_quizzes(user_id, page, per_page)
        return jsonify(quizzes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@quiz_bp.route('/<quiz_id>/attempts', methods=['GET'])
def get_quiz_attempts(quiz_id):
    """Get all attempts for a quiz"""
    try:
        attempts = quiz_service.get_quiz_attempts(quiz_id)
        return jsonify({'attempts': attempts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@quiz_bp.route('/<quiz_id>', methods=['DELETE'])
def delete_quiz(quiz_id):
    """Delete a quiz"""
    try:
        result = quiz_service.delete_quiz(quiz_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@quiz_bp.route('/validate', methods=['POST'])
def validate_question():
    """Validate a single question/answer"""
    try:
        data = request.json
        
        result = quiz_service.validate_answer(
            question=data.get('question'),
            user_answer=data.get('answer'),
            correct_answer=data.get('correct_answer')
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@quiz_bp.route('/export/<quiz_id>', methods=['GET'])
def export_quiz(quiz_id):
    """Export quiz to various formats"""
    try:
        format_type = request.args.get('format', 'json')
        
        result = quiz_service.export_quiz(quiz_id, format_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
