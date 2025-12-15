"""
Analytics Routes - API endpoints for statistics and reporting
"""

from flask import Blueprint, request, jsonify, send_file
from services import AnalyticsService
import io

analytics_bp = Blueprint('analytics', __name__)
analytics_service = AnalyticsService()


@analytics_bp.route('/user/<user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    """Get comprehensive user statistics"""
    try:
        stats = analytics_service.get_user_stats(user_id)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/user/<user_id>/performance/difficulty', methods=['GET'])
def get_performance_by_difficulty(user_id):
    """Get performance broken down by difficulty"""
    try:
        performance = analytics_service.get_performance_by_difficulty(user_id)
        return jsonify({'performance': performance})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/user/<user_id>/performance/type', methods=['GET'])
def get_performance_by_type(user_id):
    """Get performance broken down by question type"""
    try:
        performance = analytics_service.get_performance_by_type(user_id)
        return jsonify({'performance': performance})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/user/<user_id>/performance/topic', methods=['GET'])
def get_performance_by_topic(user_id):
    """Get performance broken down by topic"""
    try:
        performance = analytics_service.get_performance_by_topic(user_id)
        return jsonify({'performance': performance})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/user/<user_id>/weak-areas', methods=['GET'])
def get_weak_areas(user_id):
    """Get identified weak areas for focused study"""
    try:
        limit = request.args.get('limit', 5, type=int)
        
        weak_areas = analytics_service.get_weak_areas(user_id, limit)
        return jsonify({'weak_areas': weak_areas})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/user/<user_id>/progress', methods=['GET'])
def get_progress_over_time(user_id):
    """Get progress over time"""
    try:
        days = request.args.get('days', 30, type=int)
        
        progress = analytics_service.get_progress_over_time(user_id, days)
        return jsonify({'progress': progress})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/user/<user_id>/study-time', methods=['GET'])
def get_study_time(user_id):
    """Get study time distribution"""
    try:
        days = request.args.get('days', 30, type=int)
        
        study_time = analytics_service.get_study_time(user_id, days)
        return jsonify(study_time)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/quiz/<quiz_id>/stats', methods=['GET'])
def get_quiz_stats(quiz_id):
    """Get statistics for a specific quiz"""
    try:
        stats = analytics_service.get_quiz_stats(quiz_id)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/quiz/<quiz_id>/question-analysis', methods=['GET'])
def get_question_analysis(quiz_id):
    """Get detailed analysis per question"""
    try:
        analysis = analytics_service.get_question_analysis(quiz_id)
        return jsonify({'analysis': analysis})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/user/<user_id>/recommendations', methods=['GET'])
def get_study_recommendations(user_id):
    """Get personalized study recommendations"""
    try:
        recommendations = analytics_service.get_study_recommendations(user_id)
        return jsonify({'recommendations': recommendations})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/user/<user_id>/export/pdf', methods=['GET'])
def export_results_pdf(user_id):
    """Export user results as PDF"""
    try:
        pdf_buffer = analytics_service.export_results_pdf(user_id)
        
        if not pdf_buffer:
            return jsonify({'error': 'Failed to generate PDF'}), 500
        
        pdf_buffer.seek(0)
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'quiz_results_{user_id}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/user/<user_id>/export/csv', methods=['GET'])
def export_results_csv(user_id):
    """Export user results as CSV"""
    try:
        csv_data = analytics_service.export_results_csv(user_id)
        
        if not csv_data:
            return jsonify({'error': 'Failed to generate CSV'}), 500
        
        buffer = io.StringIO(csv_data)
        return send_file(
            io.BytesIO(buffer.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'quiz_results_{user_id}.csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Teacher Analytics
@analytics_bp.route('/class/<class_id>/stats', methods=['GET'])
def get_class_stats(class_id):
    """Get class-wide statistics (teacher only)"""
    try:
        stats = analytics_service.get_class_stats(class_id)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/class/<class_id>/student-comparison', methods=['GET'])
def get_student_comparison(class_id):
    """Compare student performance in a class"""
    try:
        comparison = analytics_service.get_student_comparison(class_id)
        return jsonify({'comparison': comparison})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/class/<class_id>/export', methods=['GET'])
def export_class_results(class_id):
    """Export class results"""
    try:
        format_type = request.args.get('format', 'csv')
        
        result = analytics_service.export_class_results(class_id, format_type)
        
        if format_type == 'csv':
            return send_file(
                io.BytesIO(result.encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'class_results_{class_id}.csv'
            )
        else:
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
