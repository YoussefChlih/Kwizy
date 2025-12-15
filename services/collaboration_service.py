"""
Collaboration Service - Real-time rooms, sharing, multiplayer
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import uuid
import secrets


class CollaborationService:
    """Service for collaborative and multiplayer features"""
    
    def __init__(self, db=None, socketio=None):
        self.db = db
        self.socketio = socketio
        self._active_rooms = {}  # In-memory room state
    
    # ==================== Quiz Sharing ====================
    
    def create_share_link(
        self,
        quiz_id: str,
        user_id: str = None,
        password: str = None,
        max_attempts: int = None,
        expires_in_days: int = None,
        allow_review: bool = True,
        show_leaderboard: bool = True,
        randomize_questions: bool = False
    ) -> Dict:
        """Create a shareable link for a quiz"""
        share_code = secrets.token_urlsafe(10)
        share_id = str(uuid.uuid4())
        
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        share_data = {
            'id': share_id,
            'quiz_id': quiz_id,
            'share_code': share_code,
            'share_url': f"/quiz/shared/{share_code}",
            'password_protected': password is not None,
            'max_attempts': max_attempts,
            'expires_at': expires_at.isoformat() if expires_at else None,
            'allow_review': allow_review,
            'show_leaderboard': show_leaderboard,
            'randomize_questions': randomize_questions,
            'created_at': datetime.utcnow().isoformat()
        }
        
        if self.db:
            from models import SharedQuiz
            from werkzeug.security import generate_password_hash
            
            shared = SharedQuiz(
                id=share_id,
                quiz_id=quiz_id,
                share_code=share_code,
                share_url=share_data['share_url'],
                password_protected=password is not None,
                password_hash=generate_password_hash(password) if password else None,
                max_attempts=max_attempts,
                expires_at=expires_at,
                allow_review=allow_review,
                show_leaderboard=show_leaderboard,
                randomize_questions=randomize_questions,
                created_by=user_id
            )
            self.db.session.add(shared)
            self.db.session.commit()
        
        return share_data
    
    def get_shared_quiz(self, share_code: str, password: str = None) -> Optional[Dict]:
        """Access a shared quiz by code"""
        if self.db:
            from models import SharedQuiz, Quiz
            from werkzeug.security import check_password_hash
            
            shared = SharedQuiz.query.filter_by(share_code=share_code).first()
            
            if not shared:
                return None
            
            # Check expiration
            if shared.expires_at and shared.expires_at < datetime.utcnow():
                return {'error': 'Link expired'}
            
            # Check password
            if shared.password_protected:
                if not password or not check_password_hash(shared.password_hash, password):
                    return {'error': 'Password required', 'password_required': True}
            
            # Increment view count
            shared.view_count += 1
            self.db.session.commit()
            
            # Get quiz
            quiz = Quiz.query.get(shared.quiz_id)
            if not quiz:
                return {'error': 'Quiz not found'}
            
            return {
                'shared': shared.to_dict(),
                'quiz': quiz.to_dict(include_questions=True)
            }
        
        return None
    
    # ==================== Real-time Quiz Rooms ====================
    
    def create_room(
        self,
        quiz_id: str,
        host_id: str = None,
        name: str = None,
        max_participants: int = 50,
        question_time_limit: int = 30,
        scheduled_start: datetime = None
    ) -> Dict:
        """Create a real-time quiz room"""
        room_code = secrets.token_urlsafe(4).upper()[:6]
        room_id = str(uuid.uuid4())
        
        room_data = {
            'id': room_id,
            'quiz_id': quiz_id,
            'room_code': room_code,
            'name': name or f"Quiz Room {room_code}",
            'host_id': host_id,
            'status': 'waiting',
            'max_participants': max_participants,
            'question_time_limit': question_time_limit,
            'scheduled_start': scheduled_start.isoformat() if scheduled_start else None,
            'current_question_index': 0,
            'participants': [],
            'created_at': datetime.utcnow().isoformat()
        }
        
        if self.db:
            from models import QuizRoom
            
            room = QuizRoom(
                id=room_id,
                quiz_id=quiz_id,
                room_code=room_code,
                name=room_data['name'],
                host_id=host_id,
                max_participants=max_participants,
                question_time_limit=question_time_limit,
                scheduled_start=scheduled_start
            )
            self.db.session.add(room)
            self.db.session.commit()
        
        # Store in memory for real-time updates
        self._active_rooms[room_code] = room_data
        
        return room_data
    
    def join_room(
        self,
        room_code: str,
        user_id: str = None,
        nickname: str = None,
        avatar_emoji: str = None
    ) -> Dict:
        """Join a quiz room"""
        result = {'success': False}
        
        if self.db:
            from models import QuizRoom, RoomParticipant
            
            room = QuizRoom.query.filter_by(room_code=room_code).first()
            
            if not room:
                return {'success': False, 'error': 'Room not found'}
            
            if room.status != 'waiting':
                return {'success': False, 'error': 'Quiz already started'}
            
            if room.participants.count() >= room.max_participants:
                return {'success': False, 'error': 'Room is full'}
            
            # Create participant
            participant_id = str(uuid.uuid4())
            participant = RoomParticipant(
                id=participant_id,
                room_id=room.id,
                user_id=user_id,
                nickname=nickname or f"Player_{participant_id[:6]}",
                avatar_emoji=avatar_emoji or '👤'
            )
            self.db.session.add(participant)
            self.db.session.commit()
            
            result = {
                'success': True,
                'participant_id': participant_id,
                'room': room.to_dict(),
                'participant': participant.to_dict()
            }
            
            # Notify other participants via WebSocket
            if self.socketio:
                self.socketio.emit('participant_joined', {
                    'room_code': room_code,
                    'participant': participant.to_dict()
                }, room=room_code)
        
        return result
    
    def start_room(self, room_code: str, host_id: str) -> Dict:
        """Start a quiz room (host only)"""
        if self.db:
            from models import QuizRoom
            
            room = QuizRoom.query.filter_by(room_code=room_code).first()
            
            if not room:
                return {'success': False, 'error': 'Room not found'}
            
            if room.host_id != host_id:
                return {'success': False, 'error': 'Only host can start'}
            
            room.status = 'in_progress'
            room.started_at = datetime.utcnow()
            self.db.session.commit()
            
            # Notify all participants
            if self.socketio:
                self.socketio.emit('quiz_started', {
                    'room_code': room_code
                }, room=room_code)
            
            return {'success': True, 'room': room.to_dict()}
        
        return {'success': False}
    
    def submit_room_answer(
        self,
        room_code: str,
        participant_id: str,
        question_index: int,
        answer: str,
        time_ms: int
    ) -> Dict:
        """Submit answer in real-time room"""
        result = {'success': False}
        
        if self.db:
            from models import QuizRoom, RoomParticipant, Quiz, Question
            
            room = QuizRoom.query.filter_by(room_code=room_code).first()
            participant = RoomParticipant.query.get(participant_id)
            
            if not room or not participant:
                return {'success': False, 'error': 'Invalid room or participant'}
            
            # Get the question
            quiz = Quiz.query.get(room.quiz_id)
            questions = list(quiz.questions.order_by(Question.order_index))
            
            if question_index >= len(questions):
                return {'success': False, 'error': 'Invalid question index'}
            
            question = questions[question_index]
            
            # Check answer
            is_correct = self._check_answer(question, answer)
            
            # Calculate points (faster = more points)
            max_time = room.question_time_limit * 1000
            time_bonus = max(0, (max_time - time_ms) / max_time)
            
            if is_correct:
                points = int(100 + 100 * time_bonus)
                participant.score += points
                participant.correct_answers += 1
                participant.streak += 1
            else:
                points = 0
                participant.streak = 0
            
            self.db.session.commit()
            
            result = {
                'success': True,
                'is_correct': is_correct,
                'points_earned': points,
                'total_score': participant.score,
                'streak': participant.streak
            }
            
            # Broadcast updated scores
            if self.socketio:
                self.socketio.emit('score_update', {
                    'room_code': room_code,
                    'participant_id': participant_id,
                    'score': participant.score,
                    'streak': participant.streak
                }, room=room_code)
        
        return result
    
    def _check_answer(self, question, answer: str) -> bool:
        """Check if answer is correct"""
        import re
        
        correct = question.correct_answer.strip().upper()
        user = answer.strip().upper()
        
        if question.question_type == 'qcm':
            correct_letter = re.match(r'^([A-D])', correct)
            user_letter = re.match(r'^([A-D])', user)
            if correct_letter and user_letter:
                return correct_letter.group(1) == user_letter.group(1)
        
        return correct == user
    
    def next_question(self, room_code: str, host_id: str) -> Dict:
        """Move to next question (host only)"""
        if self.db:
            from models import QuizRoom, Quiz, Question
            
            room = QuizRoom.query.filter_by(room_code=room_code).first()
            
            if not room or room.host_id != host_id:
                return {'success': False}
            
            room.current_question_index += 1
            
            # Check if quiz is complete
            quiz = Quiz.query.get(room.quiz_id)
            total_questions = quiz.questions.count()
            
            if room.current_question_index >= total_questions:
                room.status = 'completed'
                room.ended_at = datetime.utcnow()
            
            self.db.session.commit()
            
            # Notify all participants
            if self.socketio:
                self.socketio.emit('next_question', {
                    'room_code': room_code,
                    'question_index': room.current_question_index,
                    'is_complete': room.status == 'completed'
                }, room=room_code)
            
            return {
                'success': True,
                'question_index': room.current_question_index,
                'is_complete': room.status == 'completed'
            }
        
        return {'success': False}
    
    def get_room_leaderboard(self, room_code: str) -> List[Dict]:
        """Get current leaderboard for a room"""
        leaderboard = []
        
        if self.db:
            from models import QuizRoom, RoomParticipant
            
            room = QuizRoom.query.filter_by(room_code=room_code).first()
            if room:
                participants = RoomParticipant.query.filter_by(
                    room_id=room.id
                ).order_by(RoomParticipant.score.desc()).all()
                
                for rank, p in enumerate(participants, 1):
                    leaderboard.append({
                        'rank': rank,
                        'participant_id': p.id,
                        'nickname': p.nickname,
                        'avatar_emoji': p.avatar_emoji,
                        'score': p.score,
                        'correct_answers': p.correct_answers,
                        'streak': p.streak
                    })
        
        return leaderboard
    
    def end_room(self, room_code: str) -> Dict:
        """End a quiz room and get final results"""
        if self.db:
            from models import QuizRoom
            
            room = QuizRoom.query.filter_by(room_code=room_code).first()
            if room:
                room.status = 'completed'
                room.ended_at = datetime.utcnow()
                self.db.session.commit()
                
                leaderboard = self.get_room_leaderboard(room_code)
                
                # Notify all participants
                if self.socketio:
                    self.socketio.emit('quiz_ended', {
                        'room_code': room_code,
                        'leaderboard': leaderboard
                    }, room=room_code)
                
                return {
                    'success': True,
                    'leaderboard': leaderboard
                }
        
        return {'success': False}
    
    # ==================== Global Leaderboard ====================
    
    def update_global_leaderboard(
        self,
        user_id: str = None,
        nickname: str = None,
        score: int = 0,
        quiz_id: str = None
    ) -> Dict:
        """Update global leaderboard entry"""
        if self.db:
            from models import LeaderboardEntry
            
            # Find or create entry
            if user_id:
                entry = LeaderboardEntry.query.filter_by(
                    user_id=user_id,
                    leaderboard_type='global'
                ).first()
            else:
                entry = None
            
            if not entry:
                entry = LeaderboardEntry(
                    user_id=user_id,
                    nickname=nickname,
                    leaderboard_type='global',
                    score=0
                )
                self.db.session.add(entry)
            
            entry.score += score
            entry.quizzes_completed += 1
            
            self.db.session.commit()
            
            return entry.to_dict()
        
        return {}
    
    def get_global_leaderboard(
        self,
        leaderboard_type: str = 'global',
        limit: int = 100
    ) -> List[Dict]:
        """Get global leaderboard"""
        leaderboard = []
        
        if self.db:
            from models import LeaderboardEntry, User
            
            entries = LeaderboardEntry.query.filter_by(
                leaderboard_type=leaderboard_type
            ).order_by(LeaderboardEntry.score.desc()).limit(limit).all()
            
            for rank, entry in enumerate(entries, 1):
                data = entry.to_dict()
                data['rank'] = rank
                
                if entry.user_id:
                    user = User.query.get(entry.user_id)
                    if user:
                        data['username'] = user.username
                        data['display_name'] = user.display_name
                
                leaderboard.append(data)
        
        return leaderboard
