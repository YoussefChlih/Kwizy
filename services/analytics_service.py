"""
Analytics Service - Dashboard and statistics
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class AnalyticsService:
    """Service for analytics and statistics"""
    
    def __init__(self, db=None):
        self.db = db
    
    def get_user_dashboard(
        self,
        user_id: str = None,
        session_id: str = None
    ) -> Dict:
        """Get comprehensive dashboard data for a user"""
        return {
            'overview': self.get_overview_stats(user_id, session_id),
            'progress': self.get_progress_over_time(user_id, session_id),
            'performance_by_difficulty': self.get_performance_by_difficulty(user_id, session_id),
            'performance_by_type': self.get_performance_by_question_type(user_id, session_id),
            'weak_areas': self.get_weak_areas(user_id, session_id),
            'time_stats': self.get_time_statistics(user_id, session_id),
            'recent_activity': self.get_recent_activity(user_id, session_id)
        }
    
    def get_overview_stats(
        self,
        user_id: str = None,
        session_id: str = None
    ) -> Dict:
        """Get overview statistics"""
        stats = {
            'total_quizzes': 0,
            'total_questions': 0,
            'correct_answers': 0,
            'average_score': 0,
            'total_time_minutes': 0,
            'current_streak': 0,
            'best_streak': 0
        }
        
        if self.db:
            from models import QuizAttempt, UserAnswer, UserStats
            
            # Get quiz attempts
            query = QuizAttempt.query.filter_by(status='completed')
            if user_id:
                query = query.filter_by(user_id=user_id)
            elif session_id:
                query = query.filter_by(session_id=session_id)
            
            attempts = query.all()
            
            if attempts:
                stats['total_quizzes'] = len(attempts)
                stats['total_questions'] = sum(a.total_questions or 0 for a in attempts)
                stats['correct_answers'] = sum(a.correct_count or 0 for a in attempts)
                stats['average_score'] = sum(a.score or 0 for a in attempts) / len(attempts)
                stats['total_time_minutes'] = sum(a.time_spent_seconds or 0 for a in attempts) // 60
            
            # Get streak from user stats
            if user_id:
                user_stats = UserStats.query.filter_by(user_id=user_id).first()
            else:
                user_stats = UserStats.query.filter_by(session_id=session_id).first()
            
            if user_stats:
                stats['current_streak'] = user_stats.current_streak
                stats['best_streak'] = user_stats.longest_streak
        
        return stats
    
    def get_progress_over_time(
        self,
        user_id: str = None,
        session_id: str = None,
        days: int = 30
    ) -> List[Dict]:
        """Get progress data over time"""
        progress = []
        
        if self.db:
            from models import QuizAttempt
            
            start_date = datetime.utcnow() - timedelta(days=days)
            
            query = QuizAttempt.query.filter(
                QuizAttempt.status == 'completed',
                QuizAttempt.completed_at >= start_date
            )
            
            if user_id:
                query = query.filter_by(user_id=user_id)
            elif session_id:
                query = query.filter_by(session_id=session_id)
            
            attempts = query.all()
            
            # Group by date
            by_date = defaultdict(list)
            for attempt in attempts:
                date_key = attempt.completed_at.date().isoformat()
                by_date[date_key].append(attempt)
            
            # Calculate daily stats
            current_date = start_date.date()
            end_date = datetime.utcnow().date()
            
            while current_date <= end_date:
                date_key = current_date.isoformat()
                day_attempts = by_date.get(date_key, [])
                
                if day_attempts:
                    avg_score = sum(a.score or 0 for a in day_attempts) / len(day_attempts)
                    total_questions = sum(a.total_questions or 0 for a in day_attempts)
                else:
                    avg_score = None
                    total_questions = 0
                
                progress.append({
                    'date': date_key,
                    'quizzes_completed': len(day_attempts),
                    'questions_answered': total_questions,
                    'average_score': avg_score
                })
                
                current_date += timedelta(days=1)
        
        return progress
    
    def get_performance_by_difficulty(
        self,
        user_id: str = None,
        session_id: str = None
    ) -> Dict:
        """Get performance breakdown by difficulty level"""
        performance = {
            'facile': {'correct': 0, 'total': 0, 'percentage': 0},
            'moyen': {'correct': 0, 'total': 0, 'percentage': 0},
            'difficile': {'correct': 0, 'total': 0, 'percentage': 0}
        }
        
        if self.db:
            from models import QuizAttempt, UserAnswer, Question
            
            query = QuizAttempt.query.filter_by(status='completed')
            if user_id:
                query = query.filter_by(user_id=user_id)
            elif session_id:
                query = query.filter_by(session_id=session_id)
            
            attempts = query.all()
            
            for attempt in attempts:
                answers = UserAnswer.query.filter_by(attempt_id=attempt.id).all()
                
                for answer in answers:
                    question = Question.query.get(answer.question_id)
                    if question:
                        diff = question.difficulty or 'moyen'
                        if diff in performance:
                            performance[diff]['total'] += 1
                            if answer.is_correct:
                                performance[diff]['correct'] += 1
            
            # Calculate percentages
            for diff in performance:
                if performance[diff]['total'] > 0:
                    performance[diff]['percentage'] = (
                        performance[diff]['correct'] / performance[diff]['total'] * 100
                    )
        
        return performance
    
    def get_performance_by_question_type(
        self,
        user_id: str = None,
        session_id: str = None
    ) -> Dict:
        """Get performance breakdown by question type"""
        performance = {}
        
        if self.db:
            from models import QuizAttempt, UserAnswer, Question
            
            query = QuizAttempt.query.filter_by(status='completed')
            if user_id:
                query = query.filter_by(user_id=user_id)
            elif session_id:
                query = query.filter_by(session_id=session_id)
            
            attempts = query.all()
            
            for attempt in attempts:
                answers = UserAnswer.query.filter_by(attempt_id=attempt.id).all()
                
                for answer in answers:
                    question = Question.query.get(answer.question_id)
                    if question:
                        q_type = question.question_type or 'qcm'
                        
                        if q_type not in performance:
                            performance[q_type] = {'correct': 0, 'total': 0, 'percentage': 0}
                        
                        performance[q_type]['total'] += 1
                        if answer.is_correct:
                            performance[q_type]['correct'] += 1
            
            # Calculate percentages
            for q_type in performance:
                if performance[q_type]['total'] > 0:
                    performance[q_type]['percentage'] = (
                        performance[q_type]['correct'] / performance[q_type]['total'] * 100
                    )
        
        return performance
    
    def get_weak_areas(
        self,
        user_id: str = None,
        session_id: str = None,
        limit: int = 5
    ) -> List[Dict]:
        """Identify weak areas based on incorrect answers"""
        weak_areas = []
        
        if self.db:
            from models import QuizAttempt, UserAnswer, Question
            
            # Get recent incorrect answers
            query = QuizAttempt.query.filter_by(status='completed')
            if user_id:
                query = query.filter_by(user_id=user_id)
            elif session_id:
                query = query.filter_by(session_id=session_id)
            
            attempts = query.order_by(QuizAttempt.completed_at.desc()).limit(20).all()
            
            # Collect keywords from incorrect answers
            keyword_errors = defaultdict(int)
            
            for attempt in attempts:
                answers = UserAnswer.query.filter_by(
                    attempt_id=attempt.id,
                    is_correct=False
                ).all()
                
                for answer in answers:
                    question = Question.query.get(answer.question_id)
                    if question and question.keywords:
                        for keyword in question.keywords:
                            keyword_errors[keyword] += 1
            
            # Sort by error count
            sorted_keywords = sorted(
                keyword_errors.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            weak_areas = [
                {'topic': keyword, 'error_count': count}
                for keyword, count in sorted_keywords[:limit]
            ]
        
        return weak_areas
    
    def get_time_statistics(
        self,
        user_id: str = None,
        session_id: str = None
    ) -> Dict:
        """Get time-related statistics"""
        stats = {
            'average_time_per_question': 0,
            'average_quiz_duration': 0,
            'fastest_quiz': None,
            'time_by_difficulty': {
                'facile': 0,
                'moyen': 0,
                'difficile': 0
            }
        }
        
        if self.db:
            from models import QuizAttempt, UserAnswer, Question
            
            query = QuizAttempt.query.filter_by(status='completed')
            if user_id:
                query = query.filter_by(user_id=user_id)
            elif session_id:
                query = query.filter_by(session_id=session_id)
            
            attempts = query.all()
            
            if attempts:
                # Average quiz duration
                durations = [a.time_spent_seconds for a in attempts if a.time_spent_seconds]
                if durations:
                    stats['average_quiz_duration'] = sum(durations) / len(durations)
                    stats['fastest_quiz'] = min(durations)
                
                # Time per question
                total_time = 0
                total_questions = 0
                time_by_diff = defaultdict(list)
                
                for attempt in attempts:
                    answers = UserAnswer.query.filter_by(attempt_id=attempt.id).all()
                    
                    for answer in answers:
                        if answer.time_spent_seconds:
                            total_time += answer.time_spent_seconds
                            total_questions += 1
                            
                            question = Question.query.get(answer.question_id)
                            if question:
                                diff = question.difficulty or 'moyen'
                                time_by_diff[diff].append(answer.time_spent_seconds)
                
                if total_questions > 0:
                    stats['average_time_per_question'] = total_time / total_questions
                
                # Average time by difficulty
                for diff, times in time_by_diff.items():
                    if times:
                        stats['time_by_difficulty'][diff] = sum(times) / len(times)
        
        return stats
    
    def get_recent_activity(
        self,
        user_id: str = None,
        session_id: str = None,
        limit: int = 10
    ) -> List[Dict]:
        """Get recent activity feed"""
        activity = []
        
        if self.db:
            from models import QuizAttempt, UserBadge
            
            # Recent quiz attempts
            query = QuizAttempt.query.filter_by(status='completed')
            if user_id:
                query = query.filter_by(user_id=user_id)
            elif session_id:
                query = query.filter_by(session_id=session_id)
            
            attempts = query.order_by(QuizAttempt.completed_at.desc()).limit(limit).all()
            
            for attempt in attempts:
                activity.append({
                    'type': 'quiz_completed',
                    'timestamp': attempt.completed_at.isoformat() if attempt.completed_at else None,
                    'data': {
                        'score': attempt.score,
                        'correct': attempt.correct_count,
                        'total': attempt.total_questions
                    }
                })
            
            # Recent badges
            if user_id:
                badges = UserBadge.query.filter_by(user_id=user_id).order_by(
                    UserBadge.earned_at.desc()
                ).limit(5).all()
                
                for badge in badges:
                    activity.append({
                        'type': 'badge_earned',
                        'timestamp': badge.earned_at.isoformat() if badge.earned_at else None,
                        'data': badge.to_dict()
                    })
            
            # Sort by timestamp
            activity.sort(key=lambda x: x['timestamp'] or '', reverse=True)
        
        return activity[:limit]
    
    def generate_pdf_report(
        self,
        user_id: str = None,
        session_id: str = None
    ) -> bytes:
        """Generate a PDF report of user's progress"""
        # This would use a library like reportlab or weasyprint
        # For now, return placeholder
        dashboard = self.get_user_dashboard(user_id, session_id)
        
        # TODO: Implement actual PDF generation
        report_data = {
            'generated_at': datetime.utcnow().isoformat(),
            'data': dashboard
        }
        
        import json
        return json.dumps(report_data, indent=2).encode('utf-8')
    
    def get_comparison_stats(
        self,
        user_ids: List[str]
    ) -> Dict:
        """Compare statistics across multiple users (for teachers)"""
        comparison = {}
        
        if self.db:
            for user_id in user_ids:
                comparison[user_id] = self.get_overview_stats(user_id=user_id)
        
        return comparison
