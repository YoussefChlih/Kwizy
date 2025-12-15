"""
Gamification Service - Points, badges, streaks, challenges
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import uuid


class GamificationService:
    """Service for gamification features"""
    
    # Badge definitions
    BADGES = {
        # Streak badges
        'streak_3': {
            'name': '3 Jours Consécutifs',
            'description': 'Utilisez l\'app 3 jours de suite',
            'icon': '🔥',
            'type': 'streak',
            'requirement': 3,
            'rarity': 'common',
            'points': 10
        },
        'streak_7': {
            'name': 'Semaine Parfaite',
            'description': '7 jours consécutifs d\'utilisation',
            'icon': '⭐',
            'type': 'streak',
            'requirement': 7,
            'rarity': 'rare',
            'points': 50
        },
        'streak_30': {
            'name': 'Mois d\'Excellence',
            'description': '30 jours consécutifs',
            'icon': '🏆',
            'type': 'streak',
            'requirement': 30,
            'rarity': 'legendary',
            'points': 500
        },
        # Quiz completion badges
        'first_quiz': {
            'name': 'Premier Quiz',
            'description': 'Complétez votre premier quiz',
            'icon': '🎯',
            'type': 'quiz_count',
            'requirement': 1,
            'rarity': 'common',
            'points': 5
        },
        'quiz_10': {
            'name': 'Apprenti',
            'description': 'Complétez 10 quiz',
            'icon': '📚',
            'type': 'quiz_count',
            'requirement': 10,
            'rarity': 'common',
            'points': 25
        },
        'quiz_50': {
            'name': 'Étudiant Assidu',
            'description': 'Complétez 50 quiz',
            'icon': '🎓',
            'type': 'quiz_count',
            'requirement': 50,
            'rarity': 'rare',
            'points': 100
        },
        'quiz_100': {
            'name': 'Maître du Quiz',
            'description': 'Complétez 100 quiz',
            'icon': '👑',
            'type': 'quiz_count',
            'requirement': 100,
            'rarity': 'epic',
            'points': 250
        },
        # Score badges
        'perfect_score': {
            'name': 'Score Parfait',
            'description': 'Obtenez 100% à un quiz',
            'icon': '💯',
            'type': 'perfect_score',
            'requirement': 1,
            'rarity': 'rare',
            'points': 50
        },
        'perfect_10': {
            'name': 'Perfectionniste',
            'description': '10 quiz avec score parfait',
            'icon': '🌟',
            'type': 'perfect_count',
            'requirement': 10,
            'rarity': 'epic',
            'points': 200
        },
        # Speed badges
        'speed_demon': {
            'name': 'Éclair',
            'description': 'Terminez un quiz en moins de 2 minutes',
            'icon': '⚡',
            'type': 'speed',
            'requirement': 120,
            'rarity': 'rare',
            'points': 30
        },
        # Difficulty badges
        'hard_master': {
            'name': 'Maître du Difficile',
            'description': '10 quiz difficiles réussis (>70%)',
            'icon': '🔥',
            'type': 'hard_quizzes',
            'requirement': 10,
            'rarity': 'epic',
            'points': 150
        },
        # Social badges
        'first_share': {
            'name': 'Partageur',
            'description': 'Partagez votre premier quiz',
            'icon': '🔗',
            'type': 'share',
            'requirement': 1,
            'rarity': 'common',
            'points': 15
        }
    }
    
    # Level XP requirements
    LEVEL_XP = [0, 100, 250, 500, 1000, 2000, 3500, 5500, 8000, 12000, 18000, 25000]
    
    def __init__(self, db=None):
        self.db = db
        self._init_badges()
    
    def _init_badges(self):
        """Initialize badges in database if needed"""
        if self.db:
            from models import Badge
            
            for badge_key, badge_data in self.BADGES.items():
                existing = Badge.query.filter_by(name=badge_data['name']).first()
                if not existing:
                    badge = Badge(
                        id=badge_key,
                        name=badge_data['name'],
                        description=badge_data['description'],
                        icon=badge_data['icon'],
                        badge_type=badge_data['type'],
                        requirement_value=badge_data['requirement'],
                        rarity=badge_data['rarity'],
                        points_value=badge_data['points']
                    )
                    self.db.session.add(badge)
            
            self.db.session.commit()
    
    def get_or_create_user_stats(
        self,
        user_id: str = None,
        session_id: str = None
    ) -> Dict:
        """Get or create user statistics"""
        if self.db:
            from models import UserStats
            
            if user_id:
                stats = UserStats.query.filter_by(user_id=user_id).first()
            else:
                stats = UserStats.query.filter_by(session_id=session_id).first()
            
            if not stats:
                stats = UserStats(
                    user_id=user_id,
                    session_id=session_id
                )
                self.db.session.add(stats)
                self.db.session.commit()
            
            return stats.to_dict()
        
        return {
            'total_points': 0,
            'level': 1,
            'xp': 0,
            'current_streak': 0
        }
    
    def add_points(
        self,
        user_id: str = None,
        session_id: str = None,
        points: int = 0,
        reason: str = None
    ) -> Dict:
        """Add points to user and handle level up"""
        result = {
            'points_added': points,
            'level_up': False,
            'new_level': None
        }
        
        if self.db:
            from models import UserStats
            
            if user_id:
                stats = UserStats.query.filter_by(user_id=user_id).first()
            else:
                stats = UserStats.query.filter_by(session_id=session_id).first()
            
            if stats:
                old_level = stats.level
                stats.add_points(points)
                
                if stats.level > old_level:
                    result['level_up'] = True
                    result['new_level'] = stats.level
                
                self.db.session.commit()
                result['total_points'] = stats.total_points
                result['current_xp'] = stats.xp
                result['xp_to_next'] = stats.xp_to_next_level
        
        return result
    
    def record_quiz_completion(
        self,
        user_id: str = None,
        session_id: str = None,
        score: float = 0,
        correct_count: int = 0,
        total_questions: int = 0,
        difficulty: str = 'moyen',
        time_spent_seconds: int = 0
    ) -> Dict:
        """Record quiz completion and award points/badges"""
        result = {
            'points_earned': 0,
            'badges_earned': [],
            'level_up': False
        }
        
        # Calculate points
        base_points = total_questions * 2
        
        # Bonus for score
        if score >= 90:
            base_points *= 2
        elif score >= 70:
            base_points *= 1.5
        
        # Bonus for difficulty
        if difficulty == 'difficile':
            base_points *= 1.5
        elif difficulty == 'moyen':
            base_points *= 1.2
        
        # Speed bonus
        if time_spent_seconds and time_spent_seconds < total_questions * 20:
            base_points *= 1.2
        
        points = int(base_points)
        result['points_earned'] = points
        
        # Update stats
        if self.db:
            from models import UserStats
            
            if user_id:
                stats = UserStats.query.filter_by(user_id=user_id).first()
            else:
                stats = UserStats.query.filter_by(session_id=session_id).first()
            
            if stats:
                old_level = stats.level
                
                # Add points
                stats.add_points(points)
                
                # Update quiz stats
                stats.total_quizzes_completed += 1
                stats.total_questions_answered += total_questions
                stats.total_correct_answers += correct_count
                stats.total_time_spent_seconds += time_spent_seconds or 0
                
                # Update average score
                total = stats.total_quizzes_completed
                stats.average_score = (
                    (stats.average_score * (total - 1) + score) / total
                )
                
                # Update difficulty breakdown
                if difficulty == 'facile':
                    stats.easy_correct += correct_count
                elif difficulty == 'moyen':
                    stats.medium_correct += correct_count
                else:
                    stats.hard_correct += correct_count
                
                # Update streak
                stats.update_streak()
                
                if stats.level > old_level:
                    result['level_up'] = True
                    result['new_level'] = stats.level
                
                self.db.session.commit()
        
        # Check for badges
        badges = self.check_badges(user_id, session_id, {
            'score': score,
            'time_spent': time_spent_seconds,
            'difficulty': difficulty
        })
        result['badges_earned'] = badges
        
        return result
    
    def check_badges(
        self,
        user_id: str = None,
        session_id: str = None,
        context: Dict = None
    ) -> List[Dict]:
        """Check and award badges based on current stats"""
        earned_badges = []
        
        if not self.db:
            return earned_badges
        
        from models import UserStats, UserBadge, Badge
        
        if user_id:
            stats = UserStats.query.filter_by(user_id=user_id).first()
        else:
            stats = UserStats.query.filter_by(session_id=session_id).first()
        
        if not stats:
            return earned_badges
        
        # Get already earned badges
        earned_ids = set()
        if user_id:
            earned = UserBadge.query.filter_by(user_id=user_id).all()
        else:
            earned = UserBadge.query.filter_by(session_id=session_id).all()
        
        earned_ids = {b.badge_id for b in earned}
        
        # Check each badge
        for badge_key, badge_data in self.BADGES.items():
            if badge_key in earned_ids:
                continue
            
            earned = False
            
            if badge_data['type'] == 'streak':
                if stats.current_streak >= badge_data['requirement']:
                    earned = True
            
            elif badge_data['type'] == 'quiz_count':
                if stats.total_quizzes_completed >= badge_data['requirement']:
                    earned = True
            
            elif badge_data['type'] == 'perfect_score':
                if context and context.get('score', 0) == 100:
                    earned = True
            
            elif badge_data['type'] == 'speed':
                if context and context.get('time_spent', 999) <= badge_data['requirement']:
                    earned = True
            
            if earned:
                # Award badge
                user_badge = UserBadge(
                    user_id=user_id,
                    session_id=session_id,
                    badge_id=badge_key
                )
                self.db.session.add(user_badge)
                
                # Add bonus points
                stats.add_points(badge_data['points'])
                
                earned_badges.append({
                    'id': badge_key,
                    **badge_data
                })
        
        self.db.session.commit()
        return earned_badges
    
    def get_user_badges(
        self,
        user_id: str = None,
        session_id: str = None
    ) -> List[Dict]:
        """Get all badges earned by user"""
        badges = []
        
        if self.db:
            from models import UserBadge
            
            if user_id:
                earned = UserBadge.query.filter_by(user_id=user_id).all()
            else:
                earned = UserBadge.query.filter_by(session_id=session_id).all()
            
            badges = [b.to_dict() for b in earned]
        
        return badges
    
    def get_all_badges(self) -> List[Dict]:
        """Get all available badges"""
        return [
            {'id': key, **data}
            for key, data in self.BADGES.items()
        ]
    
    def get_daily_challenge(self, date: datetime = None) -> Optional[Dict]:
        """Get the daily challenge"""
        if date is None:
            date = datetime.utcnow()
        
        if self.db:
            from models import DailyChallenge
            
            challenge = DailyChallenge.query.filter(
                DailyChallenge.active_from <= date,
                DailyChallenge.active_until >= date,
                DailyChallenge.challenge_type == 'daily'
            ).first()
            
            if challenge:
                return challenge.to_dict()
        
        # Generate a default challenge based on day
        day_of_week = date.weekday()
        
        challenges = [
            {'title': 'Quiz Marathon', 'description': 'Complétez 5 quiz aujourd\'hui', 'target': 5, 'type': 'quiz_count', 'xp': 100},
            {'title': 'Perfectionniste', 'description': 'Obtenez 100% à un quiz', 'target': 1, 'type': 'perfect_score', 'xp': 75},
            {'title': 'Rapide et Efficace', 'description': 'Terminez 3 quiz en moins de 2 minutes chacun', 'target': 3, 'type': 'speed', 'xp': 80},
            {'title': 'Maître du Difficile', 'description': 'Réussissez un quiz difficile avec >80%', 'target': 1, 'type': 'hard_quiz', 'xp': 120},
            {'title': 'Explorer', 'description': 'Essayez 3 types de questions différents', 'target': 3, 'type': 'variety', 'xp': 60},
            {'title': 'Persévérant', 'description': 'Répondez à 50 questions', 'target': 50, 'type': 'question_count', 'xp': 90},
            {'title': 'Révision du Weekend', 'description': 'Révisez 10 flashcards', 'target': 10, 'type': 'flashcard', 'xp': 70}
        ]
        
        return challenges[day_of_week]
    
    def get_weekly_challenge(self) -> Optional[Dict]:
        """Get the weekly challenge"""
        return {
            'title': 'Défi de la Semaine',
            'description': 'Complétez 20 quiz cette semaine',
            'target': 20,
            'type': 'weekly_quiz_count',
            'xp': 500,
            'points': 1000
        }
    
    def get_challenge_progress(
        self,
        user_id: str = None,
        session_id: str = None,
        challenge_id: str = None
    ) -> Dict:
        """Get user's progress on a challenge"""
        if self.db:
            from models import UserChallengeProgress
            
            if user_id:
                progress = UserChallengeProgress.query.filter_by(
                    user_id=user_id,
                    challenge_id=challenge_id
                ).first()
            else:
                progress = UserChallengeProgress.query.filter_by(
                    session_id=session_id,
                    challenge_id=challenge_id
                ).first()
            
            if progress:
                return progress.to_dict()
        
        return {
            'current_value': 0,
            'completed': False
        }
    
    def get_leaderboard(
        self,
        leaderboard_type: str = 'global',
        limit: int = 10
    ) -> List[Dict]:
        """Get leaderboard rankings"""
        leaderboard = []
        
        if self.db:
            from models import UserStats, User
            
            query = UserStats.query
            
            if leaderboard_type == 'weekly':
                query = query.order_by(UserStats.weekly_points.desc())
            elif leaderboard_type == 'monthly':
                query = query.order_by(UserStats.monthly_points.desc())
            else:
                query = query.order_by(UserStats.total_points.desc())
            
            top_users = query.limit(limit).all()
            
            for rank, stats in enumerate(top_users, 1):
                entry = {
                    'rank': rank,
                    'user_id': stats.user_id,
                    'points': stats.total_points if leaderboard_type == 'global' else (
                        stats.weekly_points if leaderboard_type == 'weekly' else stats.monthly_points
                    ),
                    'level': stats.level,
                    'streak': stats.current_streak
                }
                
                # Get user info if available
                if stats.user_id:
                    user = User.query.get(stats.user_id)
                    if user:
                        entry['username'] = user.username
                        entry['display_name'] = user.display_name
                        entry['avatar_url'] = user.avatar_url
                
                leaderboard.append(entry)
        
        return leaderboard
