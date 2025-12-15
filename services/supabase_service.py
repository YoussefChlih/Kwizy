"""
Supabase Service - Authentication and Database management
"""

import os
from typing import Dict, Optional, List
from datetime import datetime
import uuid

try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False
    print("⚠️ Supabase not installed. Run: pip install supabase")


class SupabaseService:
    """Service for Supabase authentication and database operations"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self._init_client()
    
    def _init_client(self):
        """Initialize Supabase client"""
        if not HAS_SUPABASE:
            print("⚠️ Supabase library not available")
            return
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            print("⚠️ SUPABASE_URL and SUPABASE_KEY must be set in environment")
            return
        
        try:
            self.client = create_client(url, key)
            print("✅ Supabase client initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Supabase: {e}")
    
    @property
    def is_available(self) -> bool:
        """Check if Supabase is available"""
        return self.client is not None
    
    # ==================== Authentication ====================
    
    def register(
        self,
        email: str,
        password: str,
        username: str = None,
        display_name: str = None,
        role: str = 'student'
    ) -> Dict:
        """Register a new user with Supabase Auth"""
        if not self.is_available:
            return {'error': 'Supabase not available'}
        
        try:
            # Create auth user
            response = self.client.auth.sign_up({
                'email': email,
                'password': password,
                'options': {
                    'data': {
                        'username': username or email.split('@')[0],
                        'display_name': display_name or username or email.split('@')[0],
                        'role': role
                    }
                }
            })
            
            if response.user:
                # Create user profile in database
                profile_data = {
                    'id': response.user.id,
                    'email': email,
                    'username': username or email.split('@')[0],
                    'display_name': display_name or username or email.split('@')[0],
                    'role': role,
                    'created_at': datetime.utcnow().isoformat(),
                    'settings': {
                        'font_size': 'medium',
                        'dyslexia_mode': False,
                        'dark_mode': True,
                        'preferred_language': 'fr'
                    }
                }
                
                # Insert into users table
                self.client.table('users').insert(profile_data).execute()
                
                return {
                    'success': True,
                    'user': {
                        'id': response.user.id,
                        'email': email,
                        'username': username or email.split('@')[0],
                        'display_name': display_name or username or email.split('@')[0],
                        'role': role
                    },
                    'session': {
                        'access_token': response.session.access_token if response.session else None,
                        'refresh_token': response.session.refresh_token if response.session else None
                    }
                }
            else:
                return {'error': 'Registration failed'}
                
        except Exception as e:
            error_msg = str(e)
            if 'already registered' in error_msg.lower():
                return {'error': 'Email already registered'}
            return {'error': f'Registration failed: {error_msg}'}
    
    def login(self, email: str, password: str) -> Dict:
        """Login user with email and password"""
        if not self.is_available:
            return {'error': 'Supabase not available'}
        
        try:
            response = self.client.auth.sign_in_with_password({
                'email': email,
                'password': password
            })
            
            if response.user:
                # Get user profile
                profile = self.get_user_profile(response.user.id)
                
                return {
                    'success': True,
                    'user': profile or {
                        'id': response.user.id,
                        'email': email,
                        'username': response.user.user_metadata.get('username', email.split('@')[0]),
                        'display_name': response.user.user_metadata.get('display_name', email.split('@')[0]),
                        'role': response.user.user_metadata.get('role', 'student')
                    },
                    'session': {
                        'access_token': response.session.access_token,
                        'refresh_token': response.session.refresh_token
                    }
                }
            else:
                return {'error': 'Invalid credentials'}
                
        except Exception as e:
            error_msg = str(e)
            if 'invalid' in error_msg.lower():
                return {'error': 'Invalid email or password'}
            return {'error': f'Login failed: {error_msg}'}
    
    def logout(self, access_token: str = None) -> Dict:
        """Logout user"""
        if not self.is_available:
            return {'error': 'Supabase not available'}
        
        try:
            self.client.auth.sign_out()
            return {'success': True, 'message': 'Logged out successfully'}
        except Exception as e:
            return {'error': f'Logout failed: {str(e)}'}
    
    def validate_token(self, access_token: str) -> Optional[str]:
        """Validate access token and return user_id"""
        if not self.is_available or not access_token:
            return None
        
        try:
            response = self.client.auth.get_user(access_token)
            if response and response.user:
                return response.user.id
            return None
        except Exception:
            return None
    
    def get_user_from_token(self, access_token: str) -> Optional[Dict]:
        """Get user info from access token"""
        if not self.is_available or not access_token:
            return None
        
        try:
            response = self.client.auth.get_user(access_token)
            if response and response.user:
                profile = self.get_user_profile(response.user.id)
                return profile
            return None
        except Exception:
            return None
    
    def refresh_session(self, refresh_token: str) -> Dict:
        """Refresh access token using refresh token"""
        if not self.is_available:
            return {'error': 'Supabase not available'}
        
        try:
            response = self.client.auth.refresh_session(refresh_token)
            if response.session:
                return {
                    'success': True,
                    'session': {
                        'access_token': response.session.access_token,
                        'refresh_token': response.session.refresh_token
                    }
                }
            return {'error': 'Failed to refresh session'}
        except Exception as e:
            return {'error': f'Session refresh failed: {str(e)}'}
    
    # ==================== User Profile ====================
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile from database"""
        if not self.is_available:
            return None
        
        try:
            response = self.client.table('users').select('*').eq('id', user_id).single().execute()
            if response.data:
                return response.data
            return None
        except Exception:
            return None
    
    def update_user_profile(self, user_id: str, **kwargs) -> Dict:
        """Update user profile"""
        if not self.is_available:
            return {'error': 'Supabase not available'}
        
        try:
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            response = self.client.table('users').update(update_data).eq('id', user_id).execute()
            
            if response.data:
                return {'success': True, 'user': response.data[0]}
            return {'error': 'Update failed'}
        except Exception as e:
            return {'error': f'Profile update failed: {str(e)}'}
    
    # ==================== Quiz Data ====================
    
    def save_quiz_result(self, user_id: str, quiz_data: Dict) -> Dict:
        """Save quiz result to database"""
        if not self.is_available:
            return {'error': 'Supabase not available'}
        
        try:
            result_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'quiz_title': quiz_data.get('quiz_title', 'Quiz'),
                'score': quiz_data.get('score', 0),
                'total_questions': quiz_data.get('total_questions', 0),
                'difficulty': quiz_data.get('difficulty', 'moyen'),
                'completed_at': datetime.utcnow().isoformat(),
                'answers': quiz_data.get('answers', [])
            }
            
            response = self.client.table('quiz_results').insert(result_data).execute()
            
            if response.data:
                # Update user stats
                self._update_user_stats(user_id, quiz_data)
                return {'success': True, 'result': response.data[0]}
            return {'error': 'Failed to save quiz result'}
        except Exception as e:
            return {'error': f'Save failed: {str(e)}'}
    
    def get_user_quiz_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get user's quiz history"""
        if not self.is_available:
            return []
        
        try:
            response = self.client.table('quiz_results')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('completed_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data or []
        except Exception:
            return []
    
    def _update_user_stats(self, user_id: str, quiz_data: Dict):
        """Update user statistics after quiz completion"""
        try:
            # Get current stats
            response = self.client.table('user_stats').select('*').eq('user_id', user_id).single().execute()
            
            if response.data:
                # Update existing stats
                stats = response.data
                stats['total_quizzes'] = stats.get('total_quizzes', 0) + 1
                stats['total_correct'] = stats.get('total_correct', 0) + quiz_data.get('score', 0)
                stats['total_questions_answered'] = stats.get('total_questions_answered', 0) + quiz_data.get('total_questions', 0)
                stats['xp'] = stats.get('xp', 0) + (quiz_data.get('score', 0) * 10)
                stats['updated_at'] = datetime.utcnow().isoformat()
                
                self.client.table('user_stats').update(stats).eq('user_id', user_id).execute()
            else:
                # Create new stats
                new_stats = {
                    'user_id': user_id,
                    'total_quizzes': 1,
                    'total_correct': quiz_data.get('score', 0),
                    'total_questions_answered': quiz_data.get('total_questions', 0),
                    'xp': quiz_data.get('score', 0) * 10,
                    'level': 1,
                    'streak_days': 0,
                    'created_at': datetime.utcnow().isoformat()
                }
                self.client.table('user_stats').insert(new_stats).execute()
        except Exception as e:
            print(f"Failed to update user stats: {e}")
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get user statistics"""
        if not self.is_available:
            return {}
        
        try:
            response = self.client.table('user_stats').select('*').eq('user_id', user_id).single().execute()
            return response.data or {}
        except Exception:
            return {}
    
    # ==================== Flashcards ====================
    
    def save_flashcard(self, user_id: str, flashcard_data: Dict) -> Dict:
        """Save a flashcard"""
        if not self.is_available:
            return {'error': 'Supabase not available'}
        
        try:
            card_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'question': flashcard_data.get('question'),
                'answer': flashcard_data.get('answer'),
                'deck_id': flashcard_data.get('deck_id'),
                'ease_factor': 2.5,
                'interval': 0,
                'repetitions': 0,
                'next_review': datetime.utcnow().isoformat(),
                'created_at': datetime.utcnow().isoformat()
            }
            
            response = self.client.table('flashcards').insert(card_data).execute()
            
            if response.data:
                return {'success': True, 'flashcard': response.data[0]}
            return {'error': 'Failed to save flashcard'}
        except Exception as e:
            return {'error': f'Save failed: {str(e)}'}
    
    def get_due_flashcards(self, user_id: str) -> List[Dict]:
        """Get flashcards due for review"""
        if not self.is_available:
            return []
        
        try:
            now = datetime.utcnow().isoformat()
            response = self.client.table('flashcards')\
                .select('*')\
                .eq('user_id', user_id)\
                .lte('next_review', now)\
                .execute()
            
            return response.data or []
        except Exception:
            return []


# Create a singleton instance
supabase_service = SupabaseService()
