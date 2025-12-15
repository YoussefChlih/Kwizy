"""
Document Service - Document management and processing
Handles multi-format support, OCR, URL scraping, and content analysis
"""

import os
import re
import uuid
import hashlib
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Optional imports for advanced features
try:
    import pytesseract
    from PIL import Image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_SCRAPING = True
except ImportError:
    HAS_SCRAPING = False

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    HAS_YOUTUBE = True
except ImportError:
    HAS_YOUTUBE = False


class DocumentService:
    """Service for document management"""
    
    SUPPORTED_EXTENSIONS = {
        '.pdf', '.pptx', '.ppt', '.docx', '.doc', '.txt', '.rtf',
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'  # Images for OCR
    }
    
    def __init__(self, db=None, document_processor=None, rag_system=None):
        self.db = db
        self.document_processor = document_processor
        self.rag_system = rag_system
    
    def process_document(
        self,
        file_path: str,
        original_filename: str,
        user_id: str = None,
        session_id: str = None,
        extract_concepts: bool = True
    ) -> Dict:
        """Process and store a document"""
        
        document_id = str(uuid.uuid4())
        
        # Get file info
        file_ext = os.path.splitext(original_filename)[1].lower()
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
        # Extract text based on file type
        if file_ext in {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}:
            text_content = self.extract_text_from_image(file_path)
        else:
            text_content = self.document_processor.process(file_path) if self.document_processor else None
        
        if not text_content:
            return {
                'success': False,
                'error': 'Could not extract text from document'
            }
        
        # Detect language
        detected_language = self.detect_language(text_content)
        
        # Extract key concepts
        key_concepts = []
        if extract_concepts:
            key_concepts = self.extract_key_concepts(text_content)
        
        # Generate summary
        summary = self.generate_summary(text_content)
        
        # Add to RAG system
        num_chunks = 0
        if self.rag_system:
            metadata = {
                'filename': original_filename,
                'language': detected_language
            }
            num_chunks = self.rag_system.add_document(text_content, document_id, metadata)
        
        # Store in database
        if self.db:
            from models import Document
            
            doc = Document(
                id=document_id,
                filename=document_id + file_ext,
                original_filename=original_filename,
                file_path=file_path,
                file_type=file_ext[1:],  # Remove dot
                file_size=file_size,
                text_content=text_content,
                text_length=len(text_content),
                detected_language=detected_language,
                summary=summary,
                key_concepts=key_concepts,
                user_id=user_id,
                session_id=session_id
            )
            self.db.session.add(doc)
            self.db.session.commit()
        
        return {
            'success': True,
            'document_id': document_id,
            'filename': original_filename,
            'text_length': len(text_content),
            'chunks_created': num_chunks,
            'language': detected_language,
            'key_concepts': key_concepts,
            'summary': summary
        }
    
    def extract_text_from_image(self, image_path: str) -> Optional[str]:
        """Extract text from image using OCR"""
        if not HAS_OCR:
            return None
        
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang='fra+eng')
            return text.strip()
        except Exception as e:
            print(f"OCR error: {e}")
            return None
    
    def process_url(
        self,
        url: str,
        user_id: str = None,
        session_id: str = None
    ) -> Dict:
        """Process content from a URL"""
        if not HAS_SCRAPING:
            return {
                'success': False,
                'error': 'Web scraping not available. Install requests and beautifulsoup4.'
            }
        
        try:
            # Check if it's a YouTube URL
            youtube_id = self.extract_youtube_id(url)
            if youtube_id:
                return self.process_youtube_video(youtube_id, user_id, session_id)
            
            # Regular web page
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up text
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text_content = '\n'.join(lines)
            
            # Get title
            title = soup.find('title')
            title = title.string if title else url
            
            # Create a temporary document
            document_id = str(uuid.uuid4())
            
            if self.rag_system:
                self.rag_system.add_document(text_content, document_id, {'url': url, 'title': title})
            
            if self.db:
                from models import Document
                
                doc = Document(
                    id=document_id,
                    filename=f"web_{document_id}.txt",
                    original_filename=title[:200],
                    file_path=url,
                    file_type='url',
                    text_content=text_content,
                    text_length=len(text_content),
                    title=title,
                    user_id=user_id,
                    session_id=session_id
                )
                self.db.session.add(doc)
                self.db.session.commit()
            
            return {
                'success': True,
                'document_id': document_id,
                'title': title,
                'text_length': len(text_content),
                'source': 'url'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def process_youtube_video(
        self,
        video_id: str,
        user_id: str = None,
        session_id: str = None
    ) -> Dict:
        """Process YouTube video transcript"""
        if not HAS_YOUTUBE:
            return {
                'success': False,
                'error': 'YouTube transcript API not available. Install youtube_transcript_api.'
            }
        
        try:
            # Try to get transcript in different languages
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Prefer French, then English, then any available
            transcript = None
            for lang in ['fr', 'en']:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    break
                except:
                    continue
            
            if not transcript:
                transcript = transcript_list.find_generated_transcript(['fr', 'en'])
            
            # Get the transcript text
            transcript_data = transcript.fetch()
            text_content = ' '.join([entry['text'] for entry in transcript_data])
            
            # Create document
            document_id = str(uuid.uuid4())
            title = f"YouTube Video: {video_id}"
            
            if self.rag_system:
                self.rag_system.add_document(text_content, document_id, {
                    'source': 'youtube',
                    'video_id': video_id
                })
            
            if self.db:
                from models import Document
                
                doc = Document(
                    id=document_id,
                    filename=f"youtube_{video_id}.txt",
                    original_filename=title,
                    file_path=f"https://youtube.com/watch?v={video_id}",
                    file_type='youtube',
                    text_content=text_content,
                    text_length=len(text_content),
                    title=title,
                    user_id=user_id,
                    session_id=session_id
                )
                self.db.session.add(doc)
                self.db.session.commit()
            
            return {
                'success': True,
                'document_id': document_id,
                'title': title,
                'text_length': len(text_content),
                'source': 'youtube'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def detect_language(self, text: str) -> str:
        """Detect the language of text"""
        # Simple detection based on common words
        french_words = {'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'et', 'est', 'en', 'que', 'qui', 'dans', 'pour', 'sur', 'avec', 'ce', 'cette', 'sont', 'par'}
        english_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        arabic_pattern = re.compile(r'[\u0600-\u06FF]')
        spanish_words = {'el', 'la', 'los', 'las', 'un', 'una', 'de', 'en', 'que', 'y', 'es', 'por', 'con', 'para', 'como', 'más', 'pero', 'su', 'sus'}
        
        # Check for Arabic script
        if arabic_pattern.search(text):
            return 'ar'
        
        # Count word matches
        words = set(re.findall(r'\b\w+\b', text.lower()))
        
        french_count = len(words.intersection(french_words))
        english_count = len(words.intersection(english_words))
        spanish_count = len(words.intersection(spanish_words))
        
        if french_count > english_count and french_count > spanish_count:
            return 'fr'
        elif spanish_count > english_count:
            return 'es'
        else:
            return 'en'
    
    def extract_key_concepts(self, text: str, max_concepts: int = 10) -> List[str]:
        """Extract key concepts from text using TF-IDF-like approach"""
        # Simple extraction based on noun phrases and frequency
        
        # Tokenize and clean
        words = re.findall(r'\b[a-zA-Zà-ÿÀ-Ÿ]{4,}\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'dans', 'pour', 'avec', 'cette', 'sont', 'plus', 'aussi', 'comme',
            'fait', 'faire', 'être', 'avoir', 'tout', 'tous', 'bien', 'même',
            'the', 'and', 'that', 'this', 'with', 'from', 'they', 'have', 'been',
            'which', 'their', 'will', 'would', 'there', 'what', 'about', 'into'
        }
        
        filtered_words = [w for w in words if w not in stop_words]
        
        # Count frequencies
        from collections import Counter
        word_counts = Counter(filtered_words)
        
        # Get most common
        concepts = [word for word, count in word_counts.most_common(max_concepts)]
        
        return concepts
    
    def generate_summary(self, text: str, max_length: int = 500) -> str:
        """Generate a simple extractive summary"""
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        if not sentences:
            return ""
        
        # Score sentences by position and keyword density
        scored_sentences = []
        
        # Get important words (most frequent)
        words = re.findall(r'\b[a-zA-Zà-ÿÀ-Ÿ]{4,}\b', text.lower())
        word_freq = {}
        for w in words:
            word_freq[w] = word_freq.get(w, 0) + 1
        
        for i, sentence in enumerate(sentences):
            if len(sentence) < 20:  # Skip very short sentences
                continue
            
            # Calculate score
            sentence_words = re.findall(r'\b[a-zA-Zà-ÿÀ-Ÿ]{4,}\b', sentence.lower())
            
            # Keyword score
            keyword_score = sum(word_freq.get(w, 0) for w in sentence_words)
            
            # Position score (prefer earlier sentences)
            position_score = 1.0 / (i + 1)
            
            # Length score (prefer medium-length sentences)
            length_score = min(len(sentence_words) / 20, 1.0)
            
            total_score = keyword_score * 0.5 + position_score * 0.3 + length_score * 0.2
            
            scored_sentences.append((total_score, i, sentence))
        
        # Sort by score
        scored_sentences.sort(reverse=True)
        
        # Build summary
        summary_sentences = []
        current_length = 0
        
        # Sort selected sentences by original position
        selected = sorted(scored_sentences[:5], key=lambda x: x[1])
        
        for score, pos, sentence in selected:
            if current_length + len(sentence) <= max_length:
                summary_sentences.append(sentence)
                current_length += len(sentence)
        
        return ' '.join(summary_sentences)
    
    def get_document(self, document_id: str) -> Optional[Dict]:
        """Get document by ID"""
        if self.db:
            from models import Document
            doc = Document.query.get(document_id)
            if doc:
                return doc.to_dict()
        return None
    
    def get_user_documents(
        self,
        user_id: str = None,
        session_id: str = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get documents for a user"""
        if self.db:
            from models import Document
            
            query = Document.query
            
            if user_id:
                query = query.filter_by(user_id=user_id)
            elif session_id:
                query = query.filter_by(session_id=session_id)
            
            docs = query.order_by(Document.created_at.desc()).limit(limit).all()
            return [doc.to_dict() for doc in docs]
        
        return []
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document"""
        # Remove from RAG system
        if self.rag_system:
            self.rag_system.delete_document(document_id)
        
        # Remove from database
        if self.db:
            from models import Document
            doc = Document.query.get(document_id)
            if doc:
                # Delete file if exists
                if doc.file_path and os.path.exists(doc.file_path):
                    try:
                        os.remove(doc.file_path)
                    except:
                        pass
                
                self.db.session.delete(doc)
                self.db.session.commit()
                return True
        
        return False
    
    def get_document_concepts_graph(self, document_id: str) -> Dict:
        """Generate a concept graph for a document"""
        doc = self.get_document(document_id)
        if not doc:
            return {}
        
        concepts = doc.get('key_concepts', [])
        text = doc.get('text_content', '') if self.db else ''
        
        # Build simple co-occurrence graph
        nodes = [{'id': c, 'label': c} for c in concepts]
        edges = []
        
        # Find co-occurrences in sentences
        sentences = re.split(r'(?<=[.!?])\s+', text.lower())
        
        for sentence in sentences:
            present = [c for c in concepts if c in sentence]
            for i, c1 in enumerate(present):
                for c2 in present[i+1:]:
                    edges.append({
                        'source': c1,
                        'target': c2,
                        'weight': 1
                    })
        
        # Aggregate edge weights
        edge_dict = {}
        for edge in edges:
            key = tuple(sorted([edge['source'], edge['target']]))
            if key not in edge_dict:
                edge_dict[key] = {'source': key[0], 'target': key[1], 'weight': 0}
            edge_dict[key]['weight'] += 1
        
        return {
            'nodes': nodes,
            'edges': list(edge_dict.values())
        }
