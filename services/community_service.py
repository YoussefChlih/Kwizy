"""
Community Service - Public library, ratings, comments
"""

from typing import List, Dict, Optional
from datetime import datetime
import uuid


class CommunityService:
    """Service for community features: public quizzes, ratings, comments"""
    
    def __init__(self, db=None):
        self.db = db
    
    # ==================== Public Quiz Library ====================
    
    def publish_quiz(
        self,
        quiz_id: str,
        user_id: str,
        title: str,
        description: str = None,
        category: str = None,
        tags: List[str] = None,
        language: str = 'fr',
        is_anonymous: bool = False
    ) -> Dict:
        """Publish a quiz to the public library"""
        public_id = str(uuid.uuid4())
        
        result = {
            'id': public_id,
            'quiz_id': quiz_id,
            'title': title,
            'description': description,
            'category': category,
            'tags': tags or [],
            'language': language,
            'author_id': user_id if not is_anonymous else None,
            'is_anonymous': is_anonymous,
            'status': 'published',
            'created_at': datetime.utcnow().isoformat()
        }
        
        if self.db:
            from models import PublicQuiz, Quiz, User, Tag, QuizTag
            
            # Get original quiz
            quiz = Quiz.query.get(quiz_id)
            if not quiz:
                return {'error': 'Quiz not found'}
            
            # Create public quiz entry
            public_quiz = PublicQuiz(
                id=public_id,
                quiz_id=quiz_id,
                title=title,
                description=description or quiz.description,
                category=category,
                language=language,
                author_id=user_id if not is_anonymous else None,
                is_anonymous=is_anonymous,
                question_count=quiz.questions.count(),
                difficulty_level=quiz.difficulty_level
            )
            self.db.session.add(public_quiz)
            
            # Add tags
            if tags:
                for tag_name in tags:
                    # Get or create tag
                    tag = Tag.query.filter_by(name=tag_name.lower()).first()
                    if not tag:
                        tag = Tag(name=tag_name.lower())
                        self.db.session.add(tag)
                        self.db.session.flush()
                    
                    # Link tag to quiz
                    quiz_tag = QuizTag(public_quiz_id=public_id, tag_id=tag.id)
                    self.db.session.add(quiz_tag)
            
            self.db.session.commit()
            result = public_quiz.to_dict()
        
        return result
    
    def search_public_quizzes(
        self,
        query: str = None,
        category: str = None,
        tags: List[str] = None,
        difficulty: str = None,
        language: str = None,
        sort_by: str = 'recent',
        page: int = 1,
        per_page: int = 20
    ) -> Dict:
        """Search public quiz library"""
        results = []
        total = 0
        
        if self.db:
            from models import PublicQuiz, Tag, QuizTag
            from sqlalchemy import desc, func
            
            query_builder = PublicQuiz.query.filter_by(status='published')
            
            # Text search
            if query:
                search_term = f"%{query}%"
                query_builder = query_builder.filter(
                    (PublicQuiz.title.ilike(search_term)) |
                    (PublicQuiz.description.ilike(search_term))
                )
            
            # Filter by category
            if category:
                query_builder = query_builder.filter_by(category=category)
            
            # Filter by difficulty
            if difficulty:
                query_builder = query_builder.filter_by(difficulty_level=difficulty)
            
            # Filter by language
            if language:
                query_builder = query_builder.filter_by(language=language)
            
            # Filter by tags
            if tags:
                for tag_name in tags:
                    tag = Tag.query.filter_by(name=tag_name.lower()).first()
                    if tag:
                        query_builder = query_builder.filter(
                            PublicQuiz.id.in_(
                                self.db.session.query(QuizTag.public_quiz_id).filter_by(tag_id=tag.id)
                            )
                        )
            
            # Sorting
            if sort_by == 'recent':
                query_builder = query_builder.order_by(desc(PublicQuiz.created_at))
            elif sort_by == 'popular':
                query_builder = query_builder.order_by(desc(PublicQuiz.play_count))
            elif sort_by == 'rating':
                query_builder = query_builder.order_by(desc(PublicQuiz.average_rating))
            elif sort_by == 'trending':
                query_builder = query_builder.order_by(desc(PublicQuiz.play_count * PublicQuiz.average_rating))
            
            # Get total count
            total = query_builder.count()
            
            # Pagination
            offset = (page - 1) * per_page
            public_quizzes = query_builder.offset(offset).limit(per_page).all()
            
            for pq in public_quizzes:
                results.append(pq.to_dict())
        
        return {
            'results': results,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
    
    def get_public_quiz(self, public_quiz_id: str) -> Optional[Dict]:
        """Get a public quiz by ID"""
        if self.db:
            from models import PublicQuiz
            
            pq = PublicQuiz.query.get(public_quiz_id)
            if pq:
                return pq.to_dict(include_quiz=True)
        
        return None
    
    def play_public_quiz(self, public_quiz_id: str) -> Optional[Dict]:
        """Get quiz for playing and increment play count"""
        if self.db:
            from models import PublicQuiz, Quiz
            
            pq = PublicQuiz.query.get(public_quiz_id)
            if pq:
                pq.play_count += 1
                self.db.session.commit()
                
                quiz = Quiz.query.get(pq.quiz_id)
                return {
                    'public_quiz': pq.to_dict(),
                    'quiz': quiz.to_dict(include_questions=True) if quiz else None
                }
        
        return None
    
    # ==================== Ratings ====================
    
    def rate_quiz(
        self,
        public_quiz_id: str,
        user_id: str,
        rating: int,
        review: str = None
    ) -> Dict:
        """Rate a public quiz (1-5 stars)"""
        if not 1 <= rating <= 5:
            return {'error': 'Rating must be between 1 and 5'}
        
        if self.db:
            from models import PublicQuiz, QuizRating
            
            # Check for existing rating
            existing = QuizRating.query.filter_by(
                public_quiz_id=public_quiz_id,
                user_id=user_id
            ).first()
            
            if existing:
                # Update existing rating
                existing.rating = rating
                existing.review = review
                existing.updated_at = datetime.utcnow()
            else:
                # Create new rating
                new_rating = QuizRating(
                    public_quiz_id=public_quiz_id,
                    user_id=user_id,
                    rating=rating,
                    review=review
                )
                self.db.session.add(new_rating)
            
            # Update average rating
            pq = PublicQuiz.query.get(public_quiz_id)
            if pq:
                avg_result = self.db.session.query(
                    func.avg(QuizRating.rating)
                ).filter_by(public_quiz_id=public_quiz_id).scalar()
                
                pq.average_rating = float(avg_result) if avg_result else 0
                pq.rating_count = QuizRating.query.filter_by(
                    public_quiz_id=public_quiz_id
                ).count()
            
            self.db.session.commit()
            
            return {
                'success': True,
                'rating': rating,
                'new_average': pq.average_rating,
                'total_ratings': pq.rating_count
            }
        
        return {'error': 'Database not available'}
    
    def get_quiz_ratings(
        self,
        public_quiz_id: str,
        page: int = 1,
        per_page: int = 10
    ) -> Dict:
        """Get ratings and reviews for a quiz"""
        ratings = []
        
        if self.db:
            from models import QuizRating, User
            from sqlalchemy import desc
            
            query = QuizRating.query.filter_by(
                public_quiz_id=public_quiz_id
            ).order_by(desc(QuizRating.created_at))
            
            total = query.count()
            offset = (page - 1) * per_page
            
            for r in query.offset(offset).limit(per_page).all():
                data = r.to_dict()
                
                if r.user_id:
                    user = User.query.get(r.user_id)
                    if user:
                        data['username'] = user.username
                        data['display_name'] = user.display_name
                
                ratings.append(data)
            
            return {
                'ratings': ratings,
                'total': total,
                'page': page,
                'per_page': per_page
            }
        
        return {'ratings': [], 'total': 0}
    
    # ==================== Comments ====================
    
    def add_comment(
        self,
        public_quiz_id: str,
        user_id: str,
        content: str,
        parent_comment_id: str = None
    ) -> Dict:
        """Add a comment to a public quiz"""
        if self.db:
            from models import QuizComment, PublicQuiz
            
            comment_id = str(uuid.uuid4())
            
            comment = QuizComment(
                id=comment_id,
                public_quiz_id=public_quiz_id,
                user_id=user_id,
                content=content,
                parent_comment_id=parent_comment_id
            )
            self.db.session.add(comment)
            
            # Update comment count
            pq = PublicQuiz.query.get(public_quiz_id)
            if pq:
                pq.comment_count += 1
            
            self.db.session.commit()
            
            return comment.to_dict()
        
        return {'error': 'Database not available'}
    
    def get_quiz_comments(
        self,
        public_quiz_id: str,
        page: int = 1,
        per_page: int = 20
    ) -> Dict:
        """Get comments for a quiz (threaded)"""
        comments = []
        
        if self.db:
            from models import QuizComment, User
            from sqlalchemy import desc
            
            # Get root comments
            query = QuizComment.query.filter_by(
                public_quiz_id=public_quiz_id,
                parent_comment_id=None
            ).order_by(desc(QuizComment.created_at))
            
            total = query.count()
            offset = (page - 1) * per_page
            
            for c in query.offset(offset).limit(per_page).all():
                comment_data = self._build_comment_tree(c)
                comments.append(comment_data)
            
            return {
                'comments': comments,
                'total': total,
                'page': page,
                'per_page': per_page
            }
        
        return {'comments': [], 'total': 0}
    
    def _build_comment_tree(self, comment) -> Dict:
        """Build comment with nested replies"""
        from models import QuizComment, User
        
        data = comment.to_dict()
        
        # Get author info
        if comment.user_id:
            user = User.query.get(comment.user_id)
            if user:
                data['username'] = user.username
                data['display_name'] = user.display_name
        
        # Get replies
        replies = QuizComment.query.filter_by(
            parent_comment_id=comment.id
        ).order_by(QuizComment.created_at).all()
        
        data['replies'] = [self._build_comment_tree(r) for r in replies]
        
        return data
    
    def delete_comment(self, comment_id: str, user_id: str) -> Dict:
        """Delete a comment (only author can delete)"""
        if self.db:
            from models import QuizComment
            
            comment = QuizComment.query.get(comment_id)
            if not comment:
                return {'error': 'Comment not found'}
            
            if comment.user_id != user_id:
                return {'error': 'Not authorized'}
            
            self.db.session.delete(comment)
            self.db.session.commit()
            
            return {'success': True}
        
        return {'error': 'Database not available'}
    
    # ==================== Tags ====================
    
    def get_popular_tags(self, limit: int = 20) -> List[Dict]:
        """Get most popular tags"""
        if self.db:
            from models import Tag, QuizTag
            from sqlalchemy import func, desc
            
            tag_counts = self.db.session.query(
                Tag.id,
                Tag.name,
                func.count(QuizTag.id).label('count')
            ).join(
                QuizTag, Tag.id == QuizTag.tag_id
            ).group_by(
                Tag.id, Tag.name
            ).order_by(
                desc('count')
            ).limit(limit).all()
            
            return [
                {'id': t.id, 'name': t.name, 'count': t.count}
                for t in tag_counts
            ]
        
        return []
    
    def get_categories(self) -> List[Dict]:
        """Get all quiz categories with counts"""
        if self.db:
            from models import PublicQuiz
            from sqlalchemy import func, desc
            
            categories = self.db.session.query(
                PublicQuiz.category,
                func.count(PublicQuiz.id).label('count')
            ).filter(
                PublicQuiz.category.isnot(None),
                PublicQuiz.status == 'published'
            ).group_by(
                PublicQuiz.category
            ).order_by(
                desc('count')
            ).all()
            
            return [
                {'name': c.category, 'count': c.count}
                for c in categories
            ]
        
        return []
    
    # ==================== Featured/Trending ====================
    
    def get_featured_quizzes(self, limit: int = 10) -> List[Dict]:
        """Get featured quizzes (curated)"""
        if self.db:
            from models import PublicQuiz
            
            featured = PublicQuiz.query.filter_by(
                status='published',
                is_featured=True
            ).order_by(PublicQuiz.featured_order).limit(limit).all()
            
            return [pq.to_dict() for pq in featured]
        
        return []
    
    def get_trending_quizzes(self, limit: int = 10) -> List[Dict]:
        """Get trending quizzes (based on recent activity)"""
        if self.db:
            from models import PublicQuiz
            from sqlalchemy import desc
            from datetime import timedelta
            
            # Quizzes with high play count in last 7 days
            week_ago = datetime.utcnow() - timedelta(days=7)
            
            trending = PublicQuiz.query.filter(
                PublicQuiz.status == 'published',
                PublicQuiz.created_at >= week_ago
            ).order_by(
                desc(PublicQuiz.play_count)
            ).limit(limit).all()
            
            return [pq.to_dict() for pq in trending]
        
        return []
    
    def get_recommended_for_user(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """Get personalized quiz recommendations"""
        recommendations = []
        
        if self.db:
            from models import PublicQuiz, QuizAttempt, Quiz, User
            from sqlalchemy import func, desc
            
            # Get user's played categories and tags
            user = User.query.get(user_id)
            if not user:
                return self.get_trending_quizzes(limit)
            
            # Get categories from user's quiz history
            played_categories = self.db.session.query(
                PublicQuiz.category
            ).join(
                Quiz, PublicQuiz.quiz_id == Quiz.id
            ).join(
                QuizAttempt, Quiz.id == QuizAttempt.quiz_id
            ).filter(
                QuizAttempt.user_id == user_id,
                PublicQuiz.category.isnot(None)
            ).distinct().all()
            
            category_list = [c[0] for c in played_categories]
            
            if category_list:
                # Get similar quizzes user hasn't played
                played_quiz_ids = [a.quiz_id for a in QuizAttempt.query.filter_by(user_id=user_id).all()]
                
                recommendations_query = PublicQuiz.query.filter(
                    PublicQuiz.status == 'published',
                    PublicQuiz.category.in_(category_list),
                    ~PublicQuiz.quiz_id.in_(played_quiz_ids)
                ).order_by(
                    desc(PublicQuiz.average_rating)
                ).limit(limit).all()
                
                recommendations = [pq.to_dict() for pq in recommendations_query]
            
            # Fill with trending if not enough
            if len(recommendations) < limit:
                trending = self.get_trending_quizzes(limit - len(recommendations))
                rec_ids = {r['id'] for r in recommendations}
                for t in trending:
                    if t['id'] not in rec_ids:
                        recommendations.append(t)
        
        return recommendations[:limit]
    
    # ==================== Reporting ====================
    
    def report_quiz(
        self,
        public_quiz_id: str,
        user_id: str,
        reason: str,
        details: str = None
    ) -> Dict:
        """Report a quiz for review"""
        if self.db:
            from models import QuizReport
            
            report = QuizReport(
                public_quiz_id=public_quiz_id,
                user_id=user_id,
                reason=reason,
                details=details
            )
            self.db.session.add(report)
            self.db.session.commit()
            
            return {'success': True, 'report_id': report.id}
        
        return {'error': 'Database not available'}


# SQLAlchemy func import at module level
from sqlalchemy import func
