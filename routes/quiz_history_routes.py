"""
Quiz History Routes - Quiz results, sharing, and PDF export
"""

from flask import Blueprint, request, jsonify, send_file, url_for
from services import QuizService
from datetime import datetime
import io
import uuid
import json
import os

quiz_history_bp = Blueprint('quiz_history', __name__)
quiz_service = QuizService()

# Store shared quizzes (in production, use database)
shared_quizzes = {}

# Local storage file for quiz history when Supabase is not available
HISTORY_FILE = 'instance/quiz_history.json'
STATS_FILE = 'instance/user_stats.json'

def _ensure_instance_dir():
    """Ensure instance directory exists"""
    os.makedirs('instance', exist_ok=True)

def _load_local_history():
    """Load history from local JSON file"""
    _ensure_instance_dir()
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def _save_local_history(history):
    """Save history to local JSON file"""
    _ensure_instance_dir()
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def _load_local_stats():
    """Load stats from local JSON file"""
    _ensure_instance_dir()
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def _save_local_stats(stats):
    """Save stats to local JSON file"""
    _ensure_instance_dir()
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


@quiz_history_bp.route('/user/<user_id>/history', methods=['GET'])
def get_quiz_history(user_id):
    """Get user's quiz history with answers"""
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Try to get from Supabase first
        try:
            from services.supabase_service import supabase_service
            if supabase_service.is_available:
                history = supabase_service.get_user_quiz_history(user_id, limit + offset)
                if history:
                    return jsonify({
                        'success': True,
                        'history': history[offset:offset+limit],
                        'total': len(history)
                    })
        except Exception as e:
            print(f"Supabase history error: {e}")
        
        # Fallback to local storage
        local_history = _load_local_history()
        user_history = local_history.get(user_id, [])
        
        # Sort by date, newest first
        user_history.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'history': user_history[offset:offset+limit],
            'total': len(user_history)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@quiz_history_bp.route('/quiz/save-result', methods=['POST'])
def save_quiz_result():
    """Save quiz result to history"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        quiz_data = {
            'quiz_title': data.get('quiz_title', 'Quiz'),
            'score': data.get('score', 0),
            'total_questions': data.get('total_questions', 0),
            'difficulty': data.get('difficulty', 'moyen'),
            'answers': data.get('answers', []),
            'questions': data.get('questions', [])
        }
        
        result_id = str(uuid.uuid4())
        saved_to_supabase = False
        
        # Try to save to Supabase
        try:
            from services.supabase_service import supabase_service
            if supabase_service.is_available:
                result = supabase_service.save_quiz_result(user_id, quiz_data)
                if 'error' not in result:
                    result_id = result.get('result', {}).get('id', result_id)
                    saved_to_supabase = True
        except Exception as e:
            print(f"Supabase save error: {e}")
        
        # Always save to local storage as backup
        local_history = _load_local_history()
        if user_id not in local_history:
            local_history[user_id] = []
        
        local_result = {
            'id': result_id,
            'quiz_title': quiz_data['quiz_title'],
            'score': quiz_data['score'],
            'total_questions': quiz_data['total_questions'],
            'difficulty': quiz_data['difficulty'],
            'answers': quiz_data['answers'],
            'created_at': datetime.utcnow().isoformat()
        }
        local_history[user_id].append(local_result)
        _save_local_history(local_history)
        
        # Update local stats
        _update_local_stats(user_id, quiz_data)
        
        return jsonify({
            'success': True,
            'result_id': result_id,
            'saved_to': 'supabase' if saved_to_supabase else 'local'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _update_local_stats(user_id, quiz_data):
    """Update local stats after quiz completion"""
    stats = _load_local_stats()
    
    if user_id not in stats:
        stats[user_id] = {
            'total_quizzes': 0,
            'total_correct': 0,
            'total_wrong': 0,
            'xp': 0,
            'level': 1,
            'performance_by_difficulty': {
                'facile': {'correct': 0, 'total': 0},
                'moyen': {'correct': 0, 'total': 0},
                'difficile': {'correct': 0, 'total': 0}
            }
        }
    
    user_stats = stats[user_id]
    user_stats['total_quizzes'] += 1
    user_stats['total_correct'] += quiz_data.get('score', 0)
    user_stats['total_wrong'] += (quiz_data.get('total_questions', 0) - quiz_data.get('score', 0))
    
    # XP calculation
    xp_earned = quiz_data.get('score', 0) * 10
    if quiz_data.get('score', 0) == quiz_data.get('total_questions', 0):
        xp_earned += 50  # Perfect score bonus
    user_stats['xp'] += xp_earned
    
    # Level up
    while user_stats['xp'] >= (user_stats['level'] + 1) * 100:
        user_stats['level'] += 1
    
    # Performance by difficulty
    difficulty = quiz_data.get('difficulty', 'moyen').lower()
    if difficulty in user_stats['performance_by_difficulty']:
        user_stats['performance_by_difficulty'][difficulty]['correct'] += quiz_data.get('score', 0)
        user_stats['performance_by_difficulty'][difficulty]['total'] += quiz_data.get('total_questions', 0)
    
    _save_local_stats(stats)
        
    # except Exception as e:
    #     return jsonify({'error': str(e)}), 500


@quiz_history_bp.route('/quiz/share', methods=['POST'])
def share_quiz():
    """Generate a shareable link for a quiz"""
    try:
        data = request.json
        quiz_data = data.get('quiz')
        
        if not quiz_data:
            return jsonify({'error': 'Quiz data required'}), 400
        
        # Generate unique share ID
        share_id = str(uuid.uuid4())[:8]
        
        # Store quiz data
        shared_quizzes[share_id] = {
            'quiz': quiz_data,
            'created_at': datetime.utcnow().isoformat(),
            'creator': data.get('creator_name', 'Anonymous'),
            'views': 0
        }
        
        # Generate shareable URL (use ngrok or similar for public access)
        share_url = f"/quiz/shared/{share_id}"
        
        return jsonify({
            'success': True,
            'share_id': share_id,
            'share_url': share_url,
            'full_url': request.host_url.rstrip('/') + share_url
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@quiz_history_bp.route('/quiz/shared/<share_id>', methods=['GET'])
def get_shared_quiz(share_id):
    """Get a shared quiz by ID"""
    try:
        if share_id not in shared_quizzes:
            return jsonify({'error': 'Quiz not found'}), 404
        
        quiz_info = shared_quizzes[share_id]
        quiz_info['views'] += 1
        
        return jsonify({
            'success': True,
            'quiz': quiz_info['quiz'],
            'creator': quiz_info['creator'],
            'created_at': quiz_info['created_at']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@quiz_history_bp.route('/quiz/export-pdf', methods=['POST'])
def export_quiz_pdf():
    """Export quiz as PDF"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        data = request.json
        quiz = data.get('quiz')
        include_answers = data.get('include_answers', False)
        
        if not quiz:
            return jsonify({'error': 'Quiz data required'}), 400
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                              topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        # Container for PDF elements
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#4f46e5'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        question_style = ParagraphStyle(
            'Question',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=12,
            spaceBefore=20
        )
        
        option_style = ParagraphStyle(
            'Option',
            parent=styles['Normal'],
            fontSize=11,
            leftIndent=20,
            spaceAfter=6
        )
        
        answer_style = ParagraphStyle(
            'Answer',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#10b981'),
            leftIndent=20,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        # Title
        title = Paragraph(quiz.get('quiz_title', 'Quiz'), title_style)
        elements.append(title)
        
        # Info
        info_text = f"Difficulté: {quiz.get('difficulty', 'N/A')} | Questions: {len(quiz.get('questions', []))}"
        info = Paragraph(info_text, styles['Normal'])
        elements.append(info)
        elements.append(Spacer(1, 20))
        
        # Questions
        for i, q in enumerate(quiz.get('questions', []), 1):
            # Question text
            question_text = f"<b>Question {i}:</b> {q.get('question', '')}"
            question_para = Paragraph(question_text, question_style)
            elements.append(question_para)
            
            # Options (for MCQ and True/False)
            if q.get('type') in ['qcm', 'vrai_faux']:
                options = q.get('options', [])
                for opt in options:
                    option_para = Paragraph(f"• {opt}", option_style)
                    elements.append(option_para)
            
            # Show answer if requested
            if include_answers:
                answer_text = f"<b>Réponse:</b> {q.get('correct_answer', 'N/A')}"
                answer_para = Paragraph(answer_text, answer_style)
                elements.append(answer_para)
                
                if q.get('explanation'):
                    exp_text = f"<i>Explication:</i> {q.get('explanation')}"
                    exp_para = Paragraph(exp_text, option_style)
                    elements.append(exp_para)
            
            elements.append(Spacer(1, 15))
        
        # Build PDF
        doc.build(elements)
        
        # Prepare response
        buffer.seek(0)
        filename = f"quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500


@quiz_history_bp.route('/user/guest/stats', methods=['GET'])
def get_guest_stats():
    """Get stats for guest/anonymous users"""
    try:
        # Return default stats for guests
        return jsonify({
            'success': True,
            'total_quizzes': 0,
            'total_correct': 0,
            'total_wrong': 0,
            'xp': 0,
            'level': 1,
            'streak_days': 0,
            'performance_by_difficulty': {
                'facile': {'success_rate': 0},
                'moyen': {'success_rate': 0},
                'difficile': {'success_rate': 0}
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@quiz_history_bp.route('/user/<user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    """Get stats for a specific user"""
    try:
        # Try Supabase first
        try:
            from services.supabase_service import supabase_service
            if supabase_service.is_available:
                stats = supabase_service.get_user_stats(user_id)
                if stats:
                    return jsonify({
                        'success': True,
                        **stats
                    })
        except Exception as e:
            print(f"Supabase stats error: {e}")
        
        # Fallback to local storage
        all_stats = _load_local_stats()
        user_stats = all_stats.get(user_id, {
            'total_quizzes': 0,
            'total_correct': 0,
            'total_wrong': 0,
            'xp': 0,
            'level': 1,
            'performance_by_difficulty': {
                'facile': {'correct': 0, 'total': 0},
                'moyen': {'correct': 0, 'total': 0},
                'difficile': {'correct': 0, 'total': 0}
            }
        })
        
        # Calculate success rates
        perf = user_stats.get('performance_by_difficulty', {})
        performance_formatted = {}
        for diff in ['facile', 'moyen', 'difficile']:
            diff_data = perf.get(diff, {'correct': 0, 'total': 0})
            total = diff_data.get('total', 0)
            correct = diff_data.get('correct', 0)
            performance_formatted[diff] = {
                'success_rate': round((correct / total) * 100) if total > 0 else 0
            }
        
        return jsonify({
            'success': True,
            'total_quizzes': user_stats.get('total_quizzes', 0),
            'total_correct': user_stats.get('total_correct', 0),
            'total_wrong': user_stats.get('total_wrong', 0),
            'xp': user_stats.get('xp', 0),
            'level': user_stats.get('level', 1),
            'streak_days': user_stats.get('streak_days', 0),
            'performance_by_difficulty': performance_formatted
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
