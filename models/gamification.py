"""
Gamification Models
Points, badges, streaks, challenges, levels
"""

from models.database import db, TimestampMixin
import uuid
from datetime import datetime, timedelta


class UserStats(db.Model, TimestampMixin):
    """User statistics and progression"""
    __tablename__ = 'user_stats'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), unique=True, nullable=True)
    session_id = db.Column(db.String(36), unique=True)
    
    # Points and Level
    total_points = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)
    xp_to_next_level = db.Column(db.Integer, default=100)
    
    # Streaks
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date)
    
    # Quiz stats
    total_quizzes_completed = db.Column(db.Integer, default=0)
    total_questions_answered = db.Column(db.Integer, default=0)
    total_correct_answers = db.Column(db.Integer, default=0)
    
    # Time stats
    total_time_spent_seconds = db.Column(db.Integer, default=0)
    average_score = db.Column(db.Float, default=0.0)
    
    # Difficulty breakdown
    easy_correct = db.Column(db.Integer, default=0)
    medium_correct = db.Column(db.Integer, default=0)
    hard_correct = db.Column(db.Integer, default=0)
    
    # Question type breakdown
    qcm_correct = db.Column(db.Integer, default=0)
    true_false_correct = db.Column(db.Integer, default=0)
    open_correct = db.Column(db.Integer, default=0)
    
    # Weekly/Monthly stats
    weekly_points = db.Column(db.Integer, default=0)
    monthly_points = db.Column(db.Integer, default=0)
    weekly_reset_date = db.Column(db.Date)
    monthly_reset_date = db.Column(db.Date)
    
    def add_points(self, points):
        """Add points and handle level up"""
        self.total_points += points
        self.weekly_points += points
        self.monthly_points += points
        self.xp += points
        
        # Check for level up
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
            self.xp_to_next_level = self._calculate_xp_for_level(self.level + 1)
    
    def _calculate_xp_for_level(self, level):
        """Calculate XP needed for next level (exponential growth)"""
        return int(100 * (level ** 1.5))
    
    def update_streak(self):
        """Update daily streak"""
        today = datetime.utcnow().date()
        
        if self.last_activity_date is None:
            self.current_streak = 1
        elif self.last_activity_date == today:
            pass  # Already counted today
        elif self.last_activity_date == today - timedelta(days=1):
            self.current_streak += 1
        else:
            self.current_streak = 1
        
        self.last_activity_date = today
        self.longest_streak = max(self.longest_streak, self.current_streak)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_points': self.total_points,
            'level': self.level,
            'xp': self.xp,
            'xp_to_next_level': self.xp_to_next_level,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'total_quizzes_completed': self.total_quizzes_completed,
            'total_questions_answered': self.total_questions_answered,
            'total_correct_answers': self.total_correct_answers,
            'average_score': self.average_score,
            'weekly_points': self.weekly_points,
            'monthly_points': self.monthly_points,
            'difficulty_breakdown': {
                'easy': self.easy_correct,
                'medium': self.medium_correct,
                'hard': self.hard_correct
            },
            'type_breakdown': {
                'qcm': self.qcm_correct,
                'true_false': self.true_false_correct,
                'open': self.open_correct
            }
        }


class Badge(db.Model, TimestampMixin):
    """Badge definition"""
    __tablename__ = 'badges'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Info
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # Icon class or emoji
    color = db.Column(db.String(20))  # Badge color
    
    # Requirements
    badge_type = db.Column(db.String(50))  # streak, quiz_count, score, etc.
    requirement_value = db.Column(db.Integer)  # Value needed to earn badge
    
    # Rarity
    rarity = db.Column(db.String(20), default='common')  # common, rare, epic, legendary
    points_value = db.Column(db.Integer, default=10)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'badge_type': self.badge_type,
            'requirement_value': self.requirement_value,
            'rarity': self.rarity,
            'points_value': self.points_value
        }


class UserBadge(db.Model, TimestampMixin):
    """Badges earned by users"""
    __tablename__ = 'user_badges'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(36))
    badge_id = db.Column(db.String(36), db.ForeignKey('badges.id'), nullable=False)
    
    # When earned
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Context
    quiz_id = db.Column(db.String(36), db.ForeignKey('quizzes.id'), nullable=True)
    
    # Notification status
    notified = db.Column(db.Boolean, default=False)
    
    # Relationships
    badge = db.relationship('Badge', backref='user_badges')
    
    def to_dict(self):
        return {
            'id': self.id,
            'badge': self.badge.to_dict() if self.badge else None,
            'earned_at': self.earned_at.isoformat() if self.earned_at else None,
            'quiz_id': self.quiz_id
        }


class Achievement(db.Model, TimestampMixin):
    """Achievement/milestone tracking"""
    __tablename__ = 'achievements'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Info
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    
    # Progress tracking
    achievement_type = db.Column(db.String(50))  # cumulative, milestone, special
    target_value = db.Column(db.Integer)
    
    # Rewards
    xp_reward = db.Column(db.Integer, default=0)
    badge_id = db.Column(db.String(36), db.ForeignKey('badges.id'), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'achievement_type': self.achievement_type,
            'target_value': self.target_value,
            'xp_reward': self.xp_reward,
            'badge_id': self.badge_id
        }


class UserAchievement(db.Model, TimestampMixin):
    """User progress on achievements"""
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(36))
    achievement_id = db.Column(db.String(36), db.ForeignKey('achievements.id'), nullable=False)
    
    # Progress
    current_value = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    achievement = db.relationship('Achievement', backref='user_achievements')
    
    def to_dict(self):
        return {
            'id': self.id,
            'achievement': self.achievement.to_dict() if self.achievement else None,
            'current_value': self.current_value,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'progress_percentage': (self.current_value / self.achievement.target_value * 100) if self.achievement and self.achievement.target_value else 0
        }


class DailyChallenge(db.Model, TimestampMixin):
    """Daily/Weekly challenges"""
    __tablename__ = 'daily_challenges'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Info
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Type and duration
    challenge_type = db.Column(db.String(20), default='daily')  # daily, weekly
    active_from = db.Column(db.DateTime, nullable=False)
    active_until = db.Column(db.DateTime, nullable=False)
    
    # Requirements
    requirement_type = db.Column(db.String(50))  # complete_quizzes, correct_answers, streak, etc.
    target_value = db.Column(db.Integer)
    difficulty_filter = db.Column(db.String(20))  # Optional: only count certain difficulties
    
    # Rewards
    xp_reward = db.Column(db.Integer, default=50)
    points_reward = db.Column(db.Integer, default=100)
    badge_id = db.Column(db.String(36), db.ForeignKey('badges.id'), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'challenge_type': self.challenge_type,
            'active_from': self.active_from.isoformat() if self.active_from else None,
            'active_until': self.active_until.isoformat() if self.active_until else None,
            'requirement_type': self.requirement_type,
            'target_value': self.target_value,
            'xp_reward': self.xp_reward,
            'points_reward': self.points_reward
        }


class UserChallengeProgress(db.Model, TimestampMixin):
    """User progress on challenges"""
    __tablename__ = 'user_challenge_progress'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(36))
    challenge_id = db.Column(db.String(36), db.ForeignKey('daily_challenges.id'), nullable=False)
    
    # Progress
    current_value = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    rewards_claimed = db.Column(db.Boolean, default=False)
    
    # Relationships
    challenge = db.relationship('DailyChallenge', backref='user_progress')
    
    def to_dict(self):
        return {
            'id': self.id,
            'challenge': self.challenge.to_dict() if self.challenge else None,
            'current_value': self.current_value,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'rewards_claimed': self.rewards_claimed
        }
