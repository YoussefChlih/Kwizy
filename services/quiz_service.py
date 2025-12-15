"""
Quiz Service - Core quiz functionality
Handles quiz generation, management, and adaptive features
"""

import json
import re
from typing import List, Dict, Optional
from datetime import datetime
import uuid


class QuizService:
    """Service for quiz management and generation"""
    
    def __init__(self, db=None, quiz_generator=None, rag_system=None):
        self.db = db
        self.quiz_generator = quiz_generator
        self.rag_system = rag_system
        self._quiz_cache = {}
    
    def generate_quiz(
        self,
        context: str,
        num_questions: int = 5,
        difficulty: str = 'moyen',
        question_types: List[str] = None,
        mode: str = 'practice',
        document_ids: List[str] = None,
        user_id: str = None,
        session_id: str = None,
        language: str = 'french',
        adaptive: bool = False,
        user_performance: Dict = None
    ) -> Dict:
        """Generate a quiz with various options"""
        
        # Adjust difficulty based on user performance if adaptive
        if adaptive and user_performance:
            difficulty = self._calculate_adaptive_difficulty(user_performance)
        
        # Generate quiz using the quiz generator
        if self.quiz_generator:
            quiz_data = self.quiz_generator.generate_quiz(
                context=context,
                num_questions=num_questions,
                difficulty=difficulty,
                question_types=question_types or ['qcm'],
                language=language
            )
        else:
            quiz_data = {
                'success': False,
                'error': 'Quiz generator not initialized',
                'questions': []
            }
        
        # Add metadata
        quiz_data['mode'] = mode
        quiz_data['document_ids'] = document_ids
        quiz_data['generated_at'] = datetime.utcnow().isoformat()
        quiz_data['quiz_id'] = str(uuid.uuid4())
        
        # Cache the quiz
        self._quiz_cache[quiz_data['quiz_id']] = quiz_data
        
        return quiz_data
    
    def generate_multi_document_quiz(
        self,
        document_ids: List[str],
        num_questions: int = 10,
        difficulty: str = 'moyen',
        include_comparative: bool = True,
        **kwargs
    ) -> Dict:
        """Generate quiz from multiple documents with comparative questions"""
        
        if not self.rag_system or not document_ids:
            return {'success': False, 'error': 'No documents or RAG system'}
        
        # Get context from each document
        all_context = []
        for doc_id in document_ids:
            doc_context = self.rag_system.get_full_context([doc_id])
            all_context.append(f"[Document: {doc_id}]\n{doc_context}")
        
        combined_context = "\n\n---\n\n".join(all_context)
        
        # Calculate questions per document
        questions_per_doc = num_questions // len(document_ids)
        comparative_questions = num_questions - (questions_per_doc * len(document_ids)) if include_comparative else 0
        
        # Generate regular questions
        quiz_data = self.generate_quiz(
            context=combined_context,
            num_questions=num_questions - comparative_questions,
            difficulty=difficulty,
            document_ids=document_ids,
            **kwargs
        )
        
        # Generate comparative questions if requested
        if include_comparative and comparative_questions > 0:
            comparative_prompt = self._build_comparative_prompt(document_ids, combined_context)
            comparative_quiz = self.generate_quiz(
                context=comparative_prompt,
                num_questions=comparative_questions,
                difficulty=difficulty,
                **kwargs
            )
            
            # Mark comparative questions
            for q in comparative_quiz.get('questions', []):
                q['is_comparative'] = True
                q['document_ids'] = document_ids
            
            # Merge questions
            quiz_data['questions'].extend(comparative_quiz.get('questions', []))
        
        quiz_data['is_multi_document'] = True
        return quiz_data
    
    def _build_comparative_prompt(self, document_ids: List[str], context: str) -> str:
        """Build prompt for comparative questions"""
        return f"""Based on the following documents, generate questions that COMPARE and CONTRAST
the content from different documents. Focus on:
- Similarities and differences between concepts
- How different documents approach the same topic
- Relationships between information from different sources

Documents: {', '.join(document_ids)}

Content:
{context}
"""
    
    def _calculate_adaptive_difficulty(self, user_performance: Dict) -> str:
        """Calculate difficulty based on user performance"""
        avg_score = user_performance.get('average_score', 50)
        recent_scores = user_performance.get('recent_scores', [])
        
        if recent_scores:
            # Weight recent performance more heavily
            weighted_score = sum(s * (i + 1) for i, s in enumerate(recent_scores[-5:])) / sum(range(1, min(6, len(recent_scores) + 1)))
        else:
            weighted_score = avg_score
        
        if weighted_score >= 80:
            return 'difficile'
        elif weighted_score >= 50:
            return 'moyen'
        else:
            return 'facile'
    
    def generate_follow_up_questions(
        self,
        original_question: Dict,
        user_answer: str,
        was_correct: bool,
        context: str
    ) -> List[Dict]:
        """Generate follow-up questions based on user's mistakes"""
        
        if was_correct:
            return []
        
        # Build prompt for follow-up questions
        follow_up_prompt = f"""The user answered incorrectly to this question:
Question: {original_question.get('question', '')}
Correct answer: {original_question.get('correct_answer', '')}
User's answer: {user_answer}

Generate 1-2 simpler questions that help the user understand the concept better.
Focus on the specific area where the user made a mistake.

Context: {context[:2000]}
"""
        
        if self.quiz_generator:
            follow_up = self.quiz_generator.generate_quiz(
                context=follow_up_prompt,
                num_questions=2,
                difficulty='facile',
                question_types=['qcm']
            )
            return follow_up.get('questions', [])
        
        return []
    
    def save_quiz(self, quiz_data: Dict, user_id: str = None, session_id: str = None) -> str:
        """Save quiz to database"""
        quiz_id = quiz_data.get('quiz_id', str(uuid.uuid4()))
        
        if self.db:
            from models import Quiz, Question
            
            quiz = Quiz(
                id=quiz_id,
                title=quiz_data.get('quiz_title', 'Quiz'),
                difficulty=quiz_data.get('difficulty', 'moyen'),
                question_types=quiz_data.get('question_types', []),
                num_questions=len(quiz_data.get('questions', [])),
                mode=quiz_data.get('mode', 'practice'),
                user_id=user_id,
                session_id=session_id,
                cached_data=quiz_data
            )
            
            self.db.session.add(quiz)
            
            for i, q in enumerate(quiz_data.get('questions', [])):
                question = Question(
                    quiz_id=quiz_id,
                    question_text=q.get('question', ''),
                    question_type=q.get('type', 'qcm'),
                    difficulty=q.get('difficulty', 'moyen'),
                    options=q.get('options'),
                    correct_answer=q.get('correct_answer', ''),
                    explanation=q.get('explanation', ''),
                    order_index=i
                )
                self.db.session.add(question)
            
            self.db.session.commit()
        
        return quiz_id
    
    def get_quiz(self, quiz_id: str) -> Optional[Dict]:
        """Retrieve a quiz by ID"""
        # Check cache first
        if quiz_id in self._quiz_cache:
            return self._quiz_cache[quiz_id]
        
        # Check database
        if self.db:
            from models import Quiz
            quiz = Quiz.query.get(quiz_id)
            if quiz:
                return quiz.to_dict(include_questions=True)
        
        return None
    
    def start_attempt(
        self,
        quiz_id: str,
        user_id: str = None,
        session_id: str = None,
        mode: str = 'practice'
    ) -> Dict:
        """Start a new quiz attempt"""
        attempt_id = str(uuid.uuid4())
        
        if self.db:
            from models import QuizAttempt
            
            attempt = QuizAttempt(
                id=attempt_id,
                quiz_id=quiz_id,
                user_id=user_id,
                session_id=session_id,
                mode=mode,
                status='in_progress'
            )
            self.db.session.add(attempt)
            self.db.session.commit()
        
        return {
            'attempt_id': attempt_id,
            'quiz_id': quiz_id,
            'started_at': datetime.utcnow().isoformat(),
            'status': 'in_progress'
        }
    
    def submit_answer(
        self,
        attempt_id: str,
        question_id: str,
        answer: str,
        time_spent_seconds: int = None
    ) -> Dict:
        """Submit an answer for a question"""
        
        result = {
            'attempt_id': attempt_id,
            'question_id': question_id,
            'submitted_at': datetime.utcnow().isoformat()
        }
        
        if self.db:
            from models import Question, UserAnswer
            
            question = Question.query.get(question_id)
            if question:
                is_correct = self._check_answer(question, answer)
                
                user_answer = UserAnswer(
                    attempt_id=attempt_id,
                    question_id=question_id,
                    answer_text=answer,
                    answer_option=answer if len(answer) == 1 else None,
                    is_correct=is_correct,
                    time_spent_seconds=time_spent_seconds
                )
                self.db.session.add(user_answer)
                self.db.session.commit()
                
                result['is_correct'] = is_correct
                result['correct_answer'] = question.correct_answer
                result['explanation'] = question.explanation
        
        return result
    
    def _check_answer(self, question, user_answer: str) -> bool:
        """Check if user's answer is correct"""
        correct = question.correct_answer.strip().upper()
        user = user_answer.strip().upper()
        
        if question.question_type == 'qcm':
            # Extract letter from both answers
            correct_letter = re.match(r'^([A-D])', correct)
            user_letter = re.match(r'^([A-D])', user)
            
            if correct_letter and user_letter:
                return correct_letter.group(1) == user_letter.group(1)
            return correct == user
        
        elif question.question_type == 'vrai_faux':
            correct_bool = 'vrai' in correct.lower() or 'true' in correct.lower()
            user_bool = 'vrai' in user.lower() or 'true' in user.lower()
            return correct_bool == user_bool
        
        else:
            # For open questions, use simple matching
            # Could be enhanced with semantic similarity
            return correct.lower() == user.lower()
    
    def complete_attempt(self, attempt_id: str) -> Dict:
        """Complete a quiz attempt and calculate results"""
        
        if self.db:
            from models import QuizAttempt, UserAnswer
            
            attempt = QuizAttempt.query.get(attempt_id)
            if attempt:
                answers = UserAnswer.query.filter_by(attempt_id=attempt_id).all()
                
                correct_count = sum(1 for a in answers if a.is_correct)
                total = len(answers)
                score = (correct_count / total * 100) if total > 0 else 0
                
                attempt.status = 'completed'
                attempt.completed_at = datetime.utcnow()
                attempt.score = score
                attempt.correct_count = correct_count
                attempt.total_questions = total
                
                # Calculate time spent
                if answers:
                    attempt.time_spent_seconds = sum(
                        a.time_spent_seconds or 0 for a in answers
                    )
                
                self.db.session.commit()
                
                return attempt.to_dict()
        
        return {}
    
    def get_quiz_history(
        self,
        user_id: str = None,
        session_id: str = None,
        limit: int = 20
    ) -> List[Dict]:
        """Get quiz history for a user"""
        
        if self.db:
            from models import QuizAttempt
            
            query = QuizAttempt.query
            
            if user_id:
                query = query.filter_by(user_id=user_id)
            elif session_id:
                query = query.filter_by(session_id=session_id)
            
            attempts = query.order_by(QuizAttempt.created_at.desc()).limit(limit).all()
            return [a.to_dict() for a in attempts]
        
        return []
    
    def resume_quiz(self, attempt_id: str) -> Optional[Dict]:
        """Resume an in-progress quiz attempt"""
        
        if self.db:
            from models import QuizAttempt, UserAnswer, Quiz
            
            attempt = QuizAttempt.query.get(attempt_id)
            if attempt and attempt.status == 'in_progress':
                # Get answered questions
                answered = UserAnswer.query.filter_by(attempt_id=attempt_id).all()
                answered_ids = {a.question_id for a in answered}
                
                # Get quiz with questions
                quiz = Quiz.query.get(attempt.quiz_id)
                if quiz:
                    quiz_data = quiz.to_dict(include_questions=True)
                    
                    # Mark answered questions
                    for q in quiz_data.get('questions', []):
                        if q['id'] in answered_ids:
                            q['answered'] = True
                            answer = next((a for a in answered if a.question_id == q['id']), None)
                            if answer:
                                q['user_answer'] = answer.answer_text
                    
                    return {
                        'attempt': attempt.to_dict(),
                        'quiz': quiz_data,
                        'progress': {
                            'answered': len(answered_ids),
                            'total': len(quiz_data.get('questions', []))
                        }
                    }
        
        return None


class LearningModeService:
    """Service for different learning modes"""
    
    MODES = {
        'practice': {
            'name': 'Entraînement',
            'description': 'Mode avec indices progressifs',
            'show_hints': True,
            'show_explanation_after': True,
            'allow_retries': True,
            'timed': False
        },
        'exam': {
            'name': 'Examen',
            'description': 'Mode chronométré sans aide',
            'show_hints': False,
            'show_explanation_after': False,
            'allow_retries': False,
            'timed': True,
            'default_time_per_question': 60
        },
        'discovery': {
            'name': 'Découverte',
            'description': 'Exploration libre du contenu',
            'show_hints': True,
            'show_explanation_after': True,
            'allow_retries': True,
            'timed': False,
            'show_correct_answer': True
        },
        'quick': {
            'name': 'Quiz Rapide',
            'description': 'Quiz de 2-3 minutes',
            'show_hints': False,
            'show_explanation_after': True,
            'allow_retries': False,
            'timed': True,
            'total_time_seconds': 180,
            'max_questions': 5
        }
    }
    
    @classmethod
    def get_mode_config(cls, mode: str) -> Dict:
        """Get configuration for a learning mode"""
        return cls.MODES.get(mode, cls.MODES['practice'])
    
    @classmethod
    def get_available_modes(cls) -> List[Dict]:
        """Get all available learning modes"""
        return [
            {'key': key, **config}
            for key, config in cls.MODES.items()
        ]
    
    @classmethod
    def get_hint(cls, question: Dict, hint_level: int = 1) -> Optional[str]:
        """Get progressive hints for a question"""
        
        if hint_level == 1:
            # First hint: topic area
            return f"Cette question porte sur: {question.get('keywords', ['le sujet'])[0] if question.get('keywords') else 'le document'}"
        
        elif hint_level == 2:
            # Second hint: eliminate wrong answers (for QCM)
            if question.get('type') == 'qcm' and question.get('options'):
                correct = question.get('correct_answer', 'A')[0]
                wrong_options = [opt for opt in question['options'] if not opt.startswith(correct)]
                if wrong_options:
                    eliminated = wrong_options[0]
                    return f"Indice: {eliminated.split(')')[0]}) n'est pas la bonne réponse"
        
        elif hint_level == 3:
            # Third hint: partial answer
            explanation = question.get('explanation', '')
            if explanation:
                return f"Réfléchissez à: {explanation[:100]}..."
        
        return None
