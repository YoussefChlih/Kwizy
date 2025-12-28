"""
User Service - Authentication, profiles, preferences
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
import uuid
import secrets


class UserService:
    """Service for user management, authentication, and preferences"""
    
    def __init__(self, db=None):
        self.db = db
        self._users = {}  # In-memory fallback
        self._sessions = {}  # Session tokens
    
    # ==================== Authentication ====================
    
    def register(
        self,
        username: str,
        email: str,
        password: str,
        display_name: str = None,
        role: str = 'student',
        profile_type: str = 'student',
        preferred_language: str = 'fr',
        theme: str = 'dark',
        notification_mode: str = 'all',
        study_mode: str = 'balanced'
    ) -> Dict:
        """Register a new user"""
        if self.db:
            from models import User
            from werkzeug.security import generate_password_hash
            
            # Check existing
            if User.query.filter_by(username=username).first():
                return {'error': 'Username already exists'}
            
            if User.query.filter_by(email=email).first():
                return {'error': 'Email already exists'}
            
            user_id = str(uuid.uuid4())
            user = User(
                id=user_id,
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                display_name=display_name or username,
                role=role,
                profile_type=profile_type,
                preferred_language=preferred_language,
                theme=theme,
                notification_mode=notification_mode,
                study_mode=study_mode
            )
            self.db.session.add(user)
            self.db.session.commit()
            
            # Generate session token
            token = self._create_session(user_id)
            
            return {
                'success': True,
                'user': user.to_dict(),
                'token': token
            }
        
        # In-memory fallback
        user_id = str(uuid.uuid4())
        self._users[user_id] = {
            'id': user_id,
            'username': username,
            'email': email,
            'display_name': display_name or username,
            'role': role,
            'profile_type': profile_type,
            'preferred_language': preferred_language,
            'theme': theme,
            'notification_mode': notification_mode,
            'study_mode': study_mode,
            'created_at': datetime.utcnow().isoformat()
        }
        token = self._create_session(user_id)
        return {
            'success': True,
            'user': self._users[user_id],
            'token': token
        }
    
    def login(self, username: str, password: str) -> Dict:
        """Login user"""
        if self.db:
            from models import User
            from werkzeug.security import check_password_hash
            
            user = User.query.filter(
                (User.username == username) | (User.email == username)
            ).first()
            
            if not user:
                return {'error': 'Invalid credentials'}
            
            if not check_password_hash(user.password_hash, password):
                return {'error': 'Invalid credentials'}
            
            # Update last login
            user.last_login = datetime.utcnow()
            self.db.session.commit()
            
            # Generate session token
            token = self._create_session(user.id)
            
            return {
                'success': True,
                'user': user.to_dict(),
                'token': token
            }
        
        return {'error': 'Authentication not available'}
    
    def logout(self, token: str) -> Dict:
        """Logout user (invalidate token)"""
        if token in self._sessions:
            del self._sessions[token]
            return {'success': True}
        return {'error': 'Invalid token'}
    
    def _create_session(self, user_id: str, expires_days: int = 7) -> str:
        """Create a session token"""
        token = secrets.token_urlsafe(32)
        self._sessions[token] = {
            'user_id': user_id,
            'expires_at': datetime.utcnow() + timedelta(days=expires_days)
        }
        return token
    
    def validate_token(self, token: str) -> Optional[str]:
        """Validate token and return user_id"""
        if token not in self._sessions:
            return None
        
        session = self._sessions[token]
        if session['expires_at'] < datetime.utcnow():
            del self._sessions[token]
            return None
        
        return session['user_id']
    
    def get_user_from_token(self, token: str) -> Optional[Dict]:
        """Get user from token"""
        user_id = self.validate_token(token)
        if not user_id:
            return None
        return self.get_user(user_id)
    
    # ==================== Password Management ====================
    
    def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> Dict:
        """Change user password"""
        if self.db:
            from models import User
            from werkzeug.security import check_password_hash, generate_password_hash
            
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            if not check_password_hash(user.password_hash, old_password):
                return {'error': 'Invalid current password'}
            
            user.password_hash = generate_password_hash(new_password)
            self.db.session.commit()
            
            return {'success': True}
        
        return {'error': 'Feature not available'}
    
    def request_password_reset(self, email: str) -> Dict:
        """Request password reset (send email with token)"""
        if self.db:
            from models import User
            
            user = User.query.filter_by(email=email).first()
            if not user:
                # Don't reveal if email exists
                return {'success': True, 'message': 'If email exists, reset link sent'}
            
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            user.reset_token = reset_token
            user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
            self.db.session.commit()
            
            # In production: send email with reset link
            # send_email(email, f"Reset link: /reset-password?token={reset_token}")
            
            return {'success': True, 'message': 'Reset link sent', 'token': reset_token}
        
        return {'error': 'Feature not available'}
    
    def reset_password(self, reset_token: str, new_password: str) -> Dict:
        """Reset password using token"""
        if self.db:
            from models import User
            from werkzeug.security import generate_password_hash
            
            user = User.query.filter_by(reset_token=reset_token).first()
            if not user:
                return {'error': 'Invalid reset token'}
            
            if user.reset_token_expires < datetime.utcnow():
                return {'error': 'Reset token expired'}
            
            user.password_hash = generate_password_hash(new_password)
            user.reset_token = None
            user.reset_token_expires = None
            self.db.session.commit()
            
            return {'success': True}
        
        return {'error': 'Feature not available'}
    
    # ==================== User Profile ====================
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        if self.db:
            from models import User
            
            user = User.query.get(user_id)
            if user:
                return user.to_dict()
        
        if user_id in self._users:
            return self._users[user_id]
        
        return None
    
    def update_profile(
        self,
        user_id: str,
        display_name: str = None,
        email: str = None,
        avatar_url: str = None,
        bio: str = None
    ) -> Dict:
        """Update user profile"""
        if self.db:
            from models import User
            
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            if display_name:
                user.display_name = display_name
            if email:
                # Check if email already exists
                existing = User.query.filter_by(email=email).first()
                if existing and existing.id != user_id:
                    return {'error': 'Email already in use'}
                user.email = email
            if avatar_url:
                user.avatar_url = avatar_url
            if bio is not None:
                user.bio = bio
            
            self.db.session.commit()
            return {'success': True, 'user': user.to_dict()}
        
        return {'error': 'Feature not available'}
    
    # ==================== Preferences ====================
    
    def get_preferences(self, user_id: str) -> Dict:
        """Get user preferences"""
        if self.db:
            from models import User
            import json
            
            user = User.query.get(user_id)
            if user:
                return user.preferences or self._default_preferences()
        
        return self._default_preferences()
    
    def update_preferences(self, user_id: str, preferences: Dict) -> Dict:
        """Update user preferences"""
        if self.db:
            from models import User
            
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            # Merge with existing preferences
            current = user.preferences or self._default_preferences()
            current.update(preferences)
            user.preferences = current
            
            self.db.session.commit()
            return {'success': True, 'preferences': current}
        
        return {'error': 'Feature not available'}
    
    def _default_preferences(self) -> Dict:
        """Default user preferences"""
        return {
            'language': 'fr',
            'theme': 'light',
            'font_size': 'medium',
            'default_question_count': 10,
            'default_difficulty': 'moyen',
            'default_question_types': ['qcm', 'vrai_faux', 'reponse_courte'],
            'enable_timer': True,
            'default_time_per_question': 30,
            'show_explanations': True,
            'enable_sound': True,
            'accessibility': {
                'high_contrast': False,
                'reduce_motion': False,
                'screen_reader_mode': False
            },
            'notifications': {
                'email_reminders': True,
                'streak_reminders': True,
                'new_quiz_alerts': False
            }
        }
    
    # ==================== Progress & Stats ====================
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get user statistics"""
        if self.db:
            from models import User, QuizAttempt, FlashcardReview, UserStreak
            from sqlalchemy import func
            
            user = User.query.get(user_id)
            if not user:
                return {}
            
            # Quiz stats
            quiz_stats = self.db.session.query(
                func.count(QuizAttempt.id).label('total_attempts'),
                func.avg(QuizAttempt.score).label('average_score'),
                func.max(QuizAttempt.score).label('best_score')
            ).filter_by(user_id=user_id).first()
            
            # Flashcard stats
            flashcard_stats = self.db.session.query(
                func.count(FlashcardReview.id).label('total_reviews')
            ).filter_by(user_id=user_id).first()
            
            # Streak info
            streak = UserStreak.query.filter_by(user_id=user_id).first()
            
            return {
                'user': user.to_dict(),
                'quiz_stats': {
                    'total_quizzes': user.total_quizzes,
                    'total_correct': user.total_correct,
                    'total_wrong': user.total_wrong,
                    'total_attempts': quiz_stats.total_attempts or 0,
                    'average_score': round(float(quiz_stats.average_score or 0), 1),
                    'best_score': quiz_stats.best_score or 0
                },
                'flashcard_stats': {
                    'total_reviews': flashcard_stats.total_reviews or 0
                },
                'gamification': {
                    'level': user.level,
                    'xp_points': user.xp_points,
                    'xp_to_next_level': (user.level + 1) * 100 - user.xp_points
                },
                'streak': {
                    'current': streak.current_streak if streak else 0,
                    'longest': streak.longest_streak if streak else 0
                }
            }
        
        return {}
    
    def update_progress(
        self,
        user_id: str,
        correct: int = 0,
        wrong: int = 0,
        xp_earned: int = 0
    ) -> Dict:
        """Update user progress after quiz/activity"""
        if self.db:
            from models import User
            
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            user.total_quizzes += 1
            user.total_correct += correct
            user.total_wrong += wrong
            user.xp_points += xp_earned
            
            # Level up check
            xp_needed = user.level * 100
            while user.xp_points >= xp_needed:
                user.level += 1
                xp_needed = user.level * 100
            
            self.db.session.commit()
            
            return {
                'success': True,
                'new_level': user.level,
                'new_xp': user.xp_points,
                'leveled_up': user.xp_points < xp_needed
            }
        
        return {'error': 'Feature not available'}
    
    # ==================== Learning History ====================
    
    def get_quiz_history(
        self,
        user_id: str,
        page: int = 1,
        per_page: int = 20
    ) -> Dict:
        """Get user's quiz history"""
        history = []
        
        if self.db:
            from models import QuizAttempt, Quiz
            from sqlalchemy import desc
            
            query = QuizAttempt.query.filter_by(
                user_id=user_id
            ).order_by(desc(QuizAttempt.started_at))
            
            total = query.count()
            offset = (page - 1) * per_page
            
            for attempt in query.offset(offset).limit(per_page).all():
                quiz = Quiz.query.get(attempt.quiz_id)
                history.append({
                    'attempt': attempt.to_dict(),
                    'quiz_title': quiz.title if quiz else 'Unknown',
                    'quiz_topic': quiz.topic if quiz else None
                })
            
            return {
                'history': history,
                'total': total,
                'page': page,
                'per_page': per_page
            }
        
        return {'history': [], 'total': 0}
    
    def get_saved_quizzes(self, user_id: str) -> List[Dict]:
        """Get user's saved/bookmarked quizzes"""
        saved = []
        
        if self.db:
            from models import SavedQuiz, Quiz
            from sqlalchemy import desc
            
            saved_entries = SavedQuiz.query.filter_by(
                user_id=user_id
            ).order_by(desc(SavedQuiz.saved_at)).all()
            
            for entry in saved_entries:
                quiz = Quiz.query.get(entry.quiz_id)
                if quiz:
                    saved.append({
                        'saved_id': entry.id,
                        'saved_at': entry.saved_at.isoformat(),
                        'quiz': quiz.to_dict()
                    })
        
        return saved
    
    def save_quiz(self, user_id: str, quiz_id: str) -> Dict:
        """Save/bookmark a quiz"""
        if self.db:
            from models import SavedQuiz
            
            # Check if already saved
            existing = SavedQuiz.query.filter_by(
                user_id=user_id,
                quiz_id=quiz_id
            ).first()
            
            if existing:
                return {'success': True, 'message': 'Already saved'}
            
            saved = SavedQuiz(
                user_id=user_id,
                quiz_id=quiz_id
            )
            self.db.session.add(saved)
            self.db.session.commit()
            
            return {'success': True, 'saved_id': saved.id}
        
        return {'error': 'Feature not available'}
    
    def unsave_quiz(self, user_id: str, quiz_id: str) -> Dict:
        """Remove quiz from saved"""
        if self.db:
            from models import SavedQuiz
            
            saved = SavedQuiz.query.filter_by(
                user_id=user_id,
                quiz_id=quiz_id
            ).first()
            
            if saved:
                self.db.session.delete(saved)
                self.db.session.commit()
                return {'success': True}
            
            return {'error': 'Not found'}
        
        return {'error': 'Feature not available'}
    
    # ==================== Teacher Features ====================
    
    def create_class(
        self,
        teacher_id: str,
        class_name: str,
        description: str = None
    ) -> Dict:
        """Create a class (teacher only)"""
        if self.db:
            from models import Class, User
            
            teacher = User.query.get(teacher_id)
            if not teacher or teacher.role != 'teacher':
                return {'error': 'Teacher role required'}
            
            class_id = str(uuid.uuid4())
            class_code = secrets.token_urlsafe(4).upper()[:6]
            
            new_class = Class(
                id=class_id,
                name=class_name,
                description=description,
                teacher_id=teacher_id,
                join_code=class_code
            )
            self.db.session.add(new_class)
            self.db.session.commit()
            
            return {
                'success': True,
                'class_id': class_id,
                'join_code': class_code
            }
        
        return {'error': 'Feature not available'}
    
    def join_class(self, student_id: str, class_code: str) -> Dict:
        """Join a class using code"""
        if self.db:
            from models import Class, ClassMember
            
            class_obj = Class.query.filter_by(join_code=class_code).first()
            if not class_obj:
                return {'error': 'Class not found'}
            
            # Check if already a member
            existing = ClassMember.query.filter_by(
                class_id=class_obj.id,
                user_id=student_id
            ).first()
            
            if existing:
                return {'error': 'Already a member'}
            
            member = ClassMember(
                class_id=class_obj.id,
                user_id=student_id
            )
            self.db.session.add(member)
            self.db.session.commit()
            
            return {'success': True, 'class': class_obj.to_dict()}
        
        return {'error': 'Feature not available'}
    
    def get_class_students(self, teacher_id: str, class_id: str) -> List[Dict]:
        """Get students in a class (teacher only)"""
        students = []
        
        if self.db:
            from models import Class, ClassMember, User
            
            class_obj = Class.query.get(class_id)
            if not class_obj or class_obj.teacher_id != teacher_id:
                return []
            
            for member in class_obj.members:
                user = User.query.get(member.user_id)
                if user:
                    students.append({
                        'user': user.to_dict(),
                        'joined_at': member.joined_at.isoformat()
                    })
        
        return students    
    # ==================== User Preferences ====================
    
    def update_user_preferences(self, user_id: str, preferences: Dict) -> Dict:
        """Update user preferences"""
        if self.db:
            from models import User
            
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            # Update allowed fields
            allowed_fields = [
                'preferred_language', 'theme', 'dark_mode', 'high_contrast',
                'font_size', 'dyslexia_mode', 'notification_mode', 'study_mode',
                'profile_type'
            ]
            
            for field, value in preferences.items():
                if field in allowed_fields and hasattr(user, field):
                    setattr(user, field, value)
            
            self.db.session.commit()
            return {'success': True, 'user': user.to_dict()}
        
        # In-memory fallback
        if user_id in self._users:
            self._users[user_id].update(preferences)
            return {'success': True, 'user': self._users[user_id]}
        
        return {'error': 'User not found'}
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """Get user preferences"""
        if self.db:
            from models import User
            
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            return {
                'success': True,
                'preferences': {
                    'preferred_language': user.preferred_language,
                    'theme': user.theme,
                    'dark_mode': user.dark_mode,
                    'high_contrast': user.high_contrast,
                    'font_size': user.font_size,
                    'dyslexia_mode': user.dyslexia_mode,
                    'notification_mode': user.notification_mode,
                    'study_mode': user.study_mode,
                    'profile_type': user.profile_type
                }
            }
        
        # In-memory fallback
        if user_id in self._users:
            return {'success': True, 'preferences': self._users[user_id]}
        
        return {'error': 'User not found'}