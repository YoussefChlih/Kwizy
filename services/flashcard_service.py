"""
Flashcard Service - Spaced Repetition System
Implements SM-2 algorithm for optimal learning
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import uuid


class FlashcardService:
    """Service for flashcard management and spaced repetition"""
    
    def __init__(self, db=None):
        self.db = db
        self._local_reviews = {}  # For session-based storage
    
    def create_flashcard(
        self,
        front: str,
        back: str,
        user_id: str = None,
        session_id: str = None,
        hint: str = None,
        tags: List[str] = None,
        category: str = None,
        question_id: str = None,
        document_id: str = None
    ) -> Dict:
        """Create a new flashcard"""
        flashcard_id = str(uuid.uuid4())
        
        flashcard_data = {
            'id': flashcard_id,
            'front': front,
            'back': back,
            'hint': hint,
            'tags': tags or [],
            'category': category,
            'question_id': question_id,
            'document_id': document_id,
            'created_at': datetime.utcnow().isoformat()
        }
        
        if self.db:
            from models import Flashcard
            
            flashcard = Flashcard(
                id=flashcard_id,
                front=front,
                back=back,
                hint=hint,
                tags=tags,
                category=category,
                question_id=question_id,
                document_id=document_id,
                user_id=user_id,
                session_id=session_id
            )
            self.db.session.add(flashcard)
            self.db.session.commit()
        
        return flashcard_data
    
    def create_flashcards_from_quiz(
        self,
        quiz_data: Dict,
        user_id: str = None,
        session_id: str = None
    ) -> List[Dict]:
        """Create flashcards from quiz questions"""
        flashcards = []
        
        for question in quiz_data.get('questions', []):
            front = question.get('question', '')
            back = question.get('correct_answer', '')
            
            # Add explanation to back if available
            if question.get('explanation'):
                back += f"\n\nExplication: {question['explanation']}"
            
            flashcard = self.create_flashcard(
                front=front,
                back=back,
                user_id=user_id,
                session_id=session_id,
                tags=question.get('keywords'),
                question_id=question.get('id')
            )
            flashcards.append(flashcard)
        
        return flashcards
    
    def get_flashcard(self, flashcard_id: str) -> Optional[Dict]:
        """Get a flashcard by ID"""
        if self.db:
            from models import Flashcard
            flashcard = Flashcard.query.get(flashcard_id)
            if flashcard:
                return flashcard.to_dict()
        return None
    
    def get_user_flashcards(
        self,
        user_id: str = None,
        session_id: str = None,
        category: str = None,
        tags: List[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get flashcards for a user"""
        if self.db:
            from models import Flashcard
            
            query = Flashcard.query
            
            if user_id:
                query = query.filter_by(user_id=user_id)
            elif session_id:
                query = query.filter_by(session_id=session_id)
            
            if category:
                query = query.filter_by(category=category)
            
            flashcards = query.limit(limit).all()
            return [f.to_dict() for f in flashcards]
        
        return []
    
    def get_due_flashcards(
        self,
        user_id: str = None,
        session_id: str = None,
        limit: int = 20
    ) -> List[Dict]:
        """Get flashcards due for review"""
        if self.db:
            from models import Flashcard, FlashcardReview
            
            # Get flashcards with reviews due
            now = datetime.utcnow()
            
            # Get all user's flashcards
            query = Flashcard.query
            if user_id:
                query = query.filter_by(user_id=user_id)
            elif session_id:
                query = query.filter_by(session_id=session_id)
            
            flashcards = query.all()
            
            due_flashcards = []
            for flashcard in flashcards:
                # Get latest review
                review = FlashcardReview.query.filter_by(
                    flashcard_id=flashcard.id
                ).order_by(FlashcardReview.reviewed_at.desc()).first()
                
                if review is None:
                    # Never reviewed - due now
                    due_flashcards.append({
                        **flashcard.to_dict(),
                        'is_new': True,
                        'priority': 1.0
                    })
                elif review.next_review and review.next_review <= now:
                    # Due for review
                    overdue_days = (now - review.next_review).days
                    priority = min(1.0, 0.5 + overdue_days * 0.1)
                    due_flashcards.append({
                        **flashcard.to_dict(),
                        'is_new': False,
                        'priority': priority,
                        'last_review': review.to_dict()
                    })
            
            # Sort by priority
            due_flashcards.sort(key=lambda x: x['priority'], reverse=True)
            
            return due_flashcards[:limit]
        
        return []
    
    def review_flashcard(
        self,
        flashcard_id: str,
        quality: int,
        user_id: str = None,
        session_id: str = None,
        response_time_ms: int = None
    ) -> Dict:
        """
        Record a flashcard review using SM-2 algorithm
        
        Quality ratings:
        0 - Complete blackout, no recognition
        1 - Incorrect, but upon seeing correct answer, remembered
        2 - Incorrect, but correct answer seemed easy to recall
        3 - Correct with serious difficulty
        4 - Correct after hesitation
        5 - Perfect response, instant recall
        """
        
        # Validate quality
        quality = max(0, min(5, quality))
        
        review_data = {
            'flashcard_id': flashcard_id,
            'quality': quality,
            'reviewed_at': datetime.utcnow().isoformat()
        }
        
        if self.db:
            from models import FlashcardReview
            
            # Get or create review record
            existing_review = FlashcardReview.query.filter_by(
                flashcard_id=flashcard_id,
                user_id=user_id,
                session_id=session_id
            ).order_by(FlashcardReview.reviewed_at.desc()).first()
            
            if existing_review:
                # Update existing review record
                review = FlashcardReview(
                    flashcard_id=flashcard_id,
                    user_id=user_id,
                    session_id=session_id,
                    easiness_factor=existing_review.easiness_factor,
                    interval=existing_review.interval,
                    repetitions=existing_review.repetitions,
                    response_time_ms=response_time_ms
                )
            else:
                # Create new review record
                review = FlashcardReview(
                    flashcard_id=flashcard_id,
                    user_id=user_id,
                    session_id=session_id,
                    response_time_ms=response_time_ms
                )
            
            # Calculate next review using SM-2
            next_review = review.calculate_next_review(quality)
            
            self.db.session.add(review)
            self.db.session.commit()
            
            review_data = review.to_dict()
            review_data['next_review'] = next_review.isoformat()
        else:
            # Session-based calculation
            key = f"{session_id or user_id}_{flashcard_id}"
            
            if key in self._local_reviews:
                prev = self._local_reviews[key]
                ef = prev['easiness_factor']
                interval = prev['interval']
                reps = prev['repetitions']
            else:
                ef = 2.5
                interval = 1
                reps = 0
            
            # SM-2 algorithm
            ef = max(1.3, ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
            
            if quality < 3:
                reps = 0
                interval = 1
            else:
                if reps == 0:
                    interval = 1
                elif reps == 1:
                    interval = 6
                else:
                    interval = round(interval * ef)
                reps += 1
            
            next_review = datetime.utcnow() + timedelta(days=interval)
            
            self._local_reviews[key] = {
                'easiness_factor': ef,
                'interval': interval,
                'repetitions': reps,
                'last_review': datetime.utcnow(),
                'next_review': next_review
            }
            
            review_data['easiness_factor'] = ef
            review_data['interval'] = interval
            review_data['repetitions'] = reps
            review_data['next_review'] = next_review.isoformat()
        
        return review_data
    
    def get_review_stats(
        self,
        user_id: str = None,
        session_id: str = None
    ) -> Dict:
        """Get review statistics"""
        stats = {
            'total_flashcards': 0,
            'total_reviews': 0,
            'due_today': 0,
            'due_this_week': 0,
            'mastered': 0,  # Cards with interval > 21 days
            'learning': 0,  # Cards with interval 1-21 days
            'new': 0,       # Cards never reviewed
            'average_easiness': 0,
            'streak': 0
        }
        
        if self.db:
            from models import Flashcard, FlashcardReview
            
            # Get user's flashcards
            query = Flashcard.query
            if user_id:
                query = query.filter_by(user_id=user_id)
            elif session_id:
                query = query.filter_by(session_id=session_id)
            
            flashcards = query.all()
            stats['total_flashcards'] = len(flashcards)
            
            now = datetime.utcnow()
            today = now.date()
            week_from_now = now + timedelta(days=7)
            
            easiness_factors = []
            
            for flashcard in flashcards:
                review = FlashcardReview.query.filter_by(
                    flashcard_id=flashcard.id
                ).order_by(FlashcardReview.reviewed_at.desc()).first()
                
                if review is None:
                    stats['new'] += 1
                else:
                    stats['total_reviews'] += 1
                    easiness_factors.append(review.easiness_factor)
                    
                    if review.interval > 21:
                        stats['mastered'] += 1
                    else:
                        stats['learning'] += 1
                    
                    if review.next_review:
                        if review.next_review.date() <= today:
                            stats['due_today'] += 1
                        if review.next_review <= week_from_now:
                            stats['due_this_week'] += 1
            
            if easiness_factors:
                stats['average_easiness'] = sum(easiness_factors) / len(easiness_factors)
        
        return stats
    
    def create_deck(
        self,
        name: str,
        user_id: str = None,
        description: str = None,
        cards_per_session: int = 20,
        new_cards_per_day: int = 10
    ) -> Dict:
        """Create a flashcard deck"""
        deck_id = str(uuid.uuid4())
        
        if self.db:
            from models.flashcard import FlashcardDeck
            
            deck = FlashcardDeck(
                id=deck_id,
                name=name,
                description=description,
                user_id=user_id,
                cards_per_session=cards_per_session,
                new_cards_per_day=new_cards_per_day
            )
            self.db.session.add(deck)
            self.db.session.commit()
            
            return deck.to_dict()
        
        return {
            'id': deck_id,
            'name': name,
            'description': description,
            'cards_per_session': cards_per_session,
            'new_cards_per_day': new_cards_per_day
        }
    
    def add_cards_to_deck(
        self,
        deck_id: str,
        flashcard_ids: List[str]
    ) -> bool:
        """Add flashcards to a deck"""
        if self.db:
            from models.flashcard import FlashcardDeck, Flashcard
            
            deck = FlashcardDeck.query.get(deck_id)
            if deck:
                for card_id in flashcard_ids:
                    card = Flashcard.query.get(card_id)
                    if card and card not in deck.cards:
                        deck.cards.append(card)
                
                self.db.session.commit()
                return True
        
        return False
    
    def get_study_session(
        self,
        user_id: str = None,
        session_id: str = None,
        deck_id: str = None,
        max_cards: int = 20,
        max_new: int = 10
    ) -> Dict:
        """Get cards for a study session"""
        
        # Get due cards
        due_cards = self.get_due_flashcards(user_id, session_id, limit=max_cards)
        
        # Separate new and review cards
        new_cards = [c for c in due_cards if c.get('is_new')]
        review_cards = [c for c in due_cards if not c.get('is_new')]
        
        # Limit new cards
        new_cards = new_cards[:max_new]
        
        # Fill remaining with review cards
        remaining = max_cards - len(new_cards)
        review_cards = review_cards[:remaining]
        
        # Interleave cards (new cards spread throughout session)
        session_cards = []
        new_idx = 0
        review_idx = 0
        
        # Add one new card every few reviews
        new_interval = len(review_cards) // (len(new_cards) + 1) if new_cards else len(review_cards)
        
        for i in range(len(new_cards) + len(review_cards)):
            if new_idx < len(new_cards) and (review_idx >= new_interval * (new_idx + 1) or review_idx >= len(review_cards)):
                session_cards.append(new_cards[new_idx])
                new_idx += 1
            elif review_idx < len(review_cards):
                session_cards.append(review_cards[review_idx])
                review_idx += 1
        
        return {
            'cards': session_cards,
            'total': len(session_cards),
            'new_count': len(new_cards),
            'review_count': len(review_cards)
        }
    
    def get_notifications(
        self,
        user_id: str = None,
        session_id: str = None
    ) -> List[Dict]:
        """Get review notifications"""
        notifications = []
        
        stats = self.get_review_stats(user_id, session_id)
        
        if stats['due_today'] > 0:
            notifications.append({
                'type': 'review_due',
                'message': f"Vous avez {stats['due_today']} cartes à réviser aujourd'hui",
                'priority': 'high',
                'count': stats['due_today']
            })
        
        if stats['new'] > 10:
            notifications.append({
                'type': 'new_cards',
                'message': f"Vous avez {stats['new']} nouvelles cartes à apprendre",
                'priority': 'medium',
                'count': stats['new']
            })
        
        return notifications
