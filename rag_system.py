"""
Enhanced RAG (Retrieval-Augmented Generation) System
Uses ChromaDB for vector storage and Sentence Transformers for embeddings
With fallback to TF-IDF for lightweight deployment
"""

import os
import re
import math
import hashlib
import logging
from typing import List, Dict, Optional, Tuple
from collections import Counter

# Setup logging
logger = logging.getLogger(__name__)

# Try to import advanced libraries, fall back to simple implementation if not available
HAS_SENTENCE_TRANSFORMERS = False
HAS_CHROMADB = False
HAS_MISTRAL = False

try:
    from mistralai.client import MistralClient
    HAS_MISTRAL = True
except ImportError as e:
    logger.warning(f"Mistral AI not available: {e}")

def get_embeddings(text: str):
    """Get embeddings from Mistral API with fallback"""
    if HAS_MISTRAL and os.getenv('MISTRAL_API_KEY'):
        try:
            client = MistralClient(api_key=os.getenv('MISTRAL_API_KEY'))
            response = client.get_embeddings(model="mistral-embed", input=[text])
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Mistral embeddings failed: {e}, using fallback")
            return _simple_encode(text)
    else:
        return _simple_encode(text)

def _simple_encode(text: str, dim: int = 384) -> List[float]:
    """Simple hash-based encoding fallback"""
    text = text.lower()
    words = re.findall(r'\b[a-zA-Zà-ÿÀ-Ÿ0-9]+\b', text)
    
    vector = [0.0] * dim
    for word in words:
        word_hash = int(hashlib.md5(word.encode()).hexdigest(), 16)
        for i in range(min(3, len(word))):
            idx = (word_hash + i * 127) % dim
            vector[idx] += 1.0
    
    norm = sum(v * v for v in vector) ** 0.5
    if norm > 0:
        vector = [v / norm for v in vector]
    
    return vector

try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMADB = True
except ImportError:
    pass

# Only try sentence_transformers if explicitly enabled (can cause TF conflicts)
if os.environ.get('USE_SENTENCE_TRANSFORMERS', '').lower() == 'true':
    try:
        from sentence_transformers import SentenceTransformer
        HAS_SENTENCE_TRANSFORMERS = True
    except (ImportError, ValueError) as e:
        logger.warning(f"Sentence Transformers not available: {e}")
        HAS_SENTENCE_TRANSFORMERS = False


class TextChunker:
    """Split text into overlapping chunks with metadata extraction"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into overlapping chunks with metadata
        
        Args:
            text: Input text to chunk
            metadata: Additional metadata for chunks
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        if not text or not text.strip():
            return []
        
        text = text.strip()
        sentences = self._split_into_sentences(text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        current_page = self._extract_page_number(sentences[0]) if sentences else None
        current_section = self._extract_section_title(sentences[0]) if sentences else None
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # Check for page/section changes
            page_match = self._extract_page_number(sentence)
            section_match = self._extract_section_title(sentence)
            
            if page_match:
                current_page = page_match
            if section_match:
                current_section = section_match
            
            if current_length + sentence_length <= self.chunk_size:
                current_chunk.append(sentence)
                current_length += sentence_length + 1
            else:
                if current_chunk:
                    chunk_text = ' '.join(current_chunk)
                    chunk_meta = {
                        'text': chunk_text,
                        'char_count': len(chunk_text),
                        'chunk_id': len(chunks),
                        'page_number': current_page,
                        'section_title': current_section
                    }
                    if metadata:
                        chunk_meta.update(metadata)
                    chunks.append(chunk_meta)
                
                # Start new chunk with overlap
                overlap_sentences = self._get_overlap_sentences(current_chunk)
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(s) for s in current_chunk) + len(current_chunk)
        
        # Don't forget the last chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunk_meta = {
                'text': chunk_text,
                'char_count': len(chunk_text),
                'chunk_id': len(chunks),
                'page_number': current_page,
                'section_title': current_section
            }
            if metadata:
                chunk_meta.update(metadata)
            chunks.append(chunk_meta)
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap_sentences(self, sentences: List[str]) -> List[str]:
        """Get sentences for overlap"""
        if not sentences:
            return []
        
        overlap_chars = 0
        overlap_sentences = []
        
        for sentence in reversed(sentences):
            if overlap_chars + len(sentence) <= self.chunk_overlap:
                overlap_sentences.insert(0, sentence)
                overlap_chars += len(sentence)
            else:
                break
        
        return overlap_sentences
    
    def _extract_page_number(self, text: str) -> Optional[int]:
        """Extract page number from text"""
        match = re.search(r'---\s*Page\s*(\d+)\s*---', text)
        if match:
            return int(match.group(1))
        return None
    
    def _extract_section_title(self, text: str) -> Optional[str]:
        """Extract section title from text"""
        match = re.search(r'^#+\s*(.+)$', text, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None


class EmbeddingEngine:
    """Handle embeddings with fallback options"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model_name = model_name
        self.model = None
        self.use_transformers = HAS_SENTENCE_TRANSFORMERS
        
        if self.use_transformers:
            try:
                self.model = SentenceTransformer(model_name)
            except Exception as e:
                logger.warning(f"SentenceTransformer initialization failed: {e}")
                self.use_transformers = False
    
    def encode(self, texts: List[str]) -> List[List[float]]:
        """Encode texts into embeddings"""
        if self.use_transformers and self.model:
            try:
                embeddings = self.model.encode(texts, show_progress_bar=False)
                return embeddings.tolist()
            except Exception as e:
                logger.warning(f"SentenceTransformer encoding failed: {e}, using fallback")
                return [_simple_encode(text) for text in texts]
        else:
            return [_simple_encode(text) for text in texts]


class ChromaVectorStore:
    """Vector store using ChromaDB with fallback"""
    
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "quiz_documents"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_engine = EmbeddingEngine()
        self.client = None
        self.collection = None
        
        if HAS_CHROMADB:
            try:
                os.makedirs(persist_directory, exist_ok=True)
                # Use PersistentClient for data persistence
                self.client = chromadb.PersistentClient(
                    path=persist_directory,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
                self.collection = self.client.get_or_create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                print(f"ChromaDB initialized with {self.collection.count()} existing documents")
            except Exception as e:
                print(f" ChromaDB initialization failed: {e}, using in-memory storage")
                self.client = None
                self.collection = None
                self.documents = []
                self.embeddings = []
        else:
            print(" ChromaDB not available, using in-memory storage")
            self.documents = []
            self.embeddings = []
    
    def add_documents(self, chunks: List[Dict], document_id: str = None):
        """Add document chunks to the vector store"""
        if not chunks:
            return
        
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedding_engine.encode(texts)
        
        if HAS_CHROMADB:
            ids = [f"{document_id}_{chunk['chunk_id']}" for chunk in chunks]
            metadatas = []
            for chunk in chunks:
                meta = {
                    'document_id': document_id or '',
                    'chunk_id': str(chunk.get('chunk_id', 0)),
                    'page_number': str(chunk.get('page_number', '')),
                    'section_title': chunk.get('section_title', '') or '',
                    'char_count': str(chunk.get('char_count', 0))
                }
                metadatas.append(meta)
            
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
        else:
            for i, chunk in enumerate(chunks):
                chunk['document_id'] = document_id
                chunk['embedding'] = embeddings[i]
                self.documents.append(chunk)
                self.embeddings.append(embeddings[i])
    
    def search(self, query: str, top_k: int = 5, filter_document_ids: List[str] = None) -> List[Dict]:
        """Search for similar documents"""
        query_embedding = self.embedding_engine.encode([query])[0]
        
        if HAS_CHROMADB and self.collection is not None:
            where_filter = None
            if filter_document_ids:
                where_filter = {"document_id": {"$in": filter_document_ids}}
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
            
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    search_results.append({
                        'text': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'score': 1 - results['distances'][0][i] if results['distances'] else 0
                    })
            
            return search_results
        else:
            scores = []
            for i, emb in enumerate(self.embeddings):
                score = self._cosine_similarity(query_embedding, emb)
                if filter_document_ids is None or self.documents[i].get('document_id') in filter_document_ids:
                    scores.append((score, i))
            
            scores.sort(reverse=True, key=lambda x: x[0])
            
            results = []
            for score, idx in scores[:top_k]:
                doc = self.documents[idx].copy()
                doc['score'] = score
                doc.pop('embedding', None)
                results.append(doc)
            
            return results
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0
        return dot / (norm_a * norm_b)
    
    def get_all_text(self) -> str:
        """Get all document text concatenated"""
        if HAS_CHROMADB and self.collection is not None:
            results = self.collection.get(include=["documents"])
            if results['documents']:
                return '\n\n'.join(results['documents'])
            return ''
        else:
            return '\n\n'.join([doc['text'] for doc in self.documents])
    
    def get_document_texts(self, document_id: str) -> List[str]:
        """Get all texts for a specific document"""
        if HAS_CHROMADB:
            results = self.collection.get(
                where={"document_id": document_id},
                include=["documents"]
            )
            return results['documents'] if results['documents'] else []
        else:
            return [doc['text'] for doc in self.documents if doc.get('document_id') == document_id]
    
    def clear(self):
        """Clear the vector store"""
        if HAS_CHROMADB:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        else:
            self.documents = []
            self.embeddings = []
    
    def delete_document(self, document_id: str):
        """Delete a specific document from the store"""
        if HAS_CHROMADB:
            self.collection.delete(where={"document_id": document_id})
        else:
            self.documents = [d for d in self.documents if d.get('document_id') != document_id]
            self.embeddings = [d.get('embedding', []) for d in self.documents]
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        if HAS_CHROMADB:
            count = self.collection.count()
            return {
                'total_chunks': count,
                'using_chromadb': True,
                'embedding_model': self.embedding_engine.model_name
            }
        else:
            return {
                'total_chunks': len(self.documents),
                'using_chromadb': False,
                'embedding_model': 'simple_hash'
            }


class ReRanker:
    """Re-rank search results for better relevance"""
    
    def __init__(self):
        self.embedding_engine = EmbeddingEngine()
    
    def rerank(self, query: str, results: List[Dict], top_k: int = 5) -> List[Dict]:
        """Re-rank results using semantic similarity"""
        if not results:
            return []
        
        query_embedding = self.embedding_engine.encode([query])[0]
        
        scored_results = []
        for result in results:
            text = result.get('text', '')
            text_embedding = self.embedding_engine.encode([text])[0]
            
            semantic_score = self._cosine_similarity(query_embedding, text_embedding)
            keyword_score = self._keyword_overlap_score(query, text)
            
            combined_score = 0.7 * semantic_score + 0.3 * keyword_score
            
            result_copy = result.copy()
            result_copy['rerank_score'] = combined_score
            scored_results.append(result_copy)
        
        scored_results.sort(key=lambda x: x['rerank_score'], reverse=True)
        
        return scored_results[:top_k]
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity"""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0
        return dot / (norm_a * norm_b)
    
    def _keyword_overlap_score(self, query: str, text: str) -> float:
        """Calculate keyword overlap score"""
        query_words = set(re.findall(r'\b[a-zA-Zà-ÿÀ-Ÿ]+\b', query.lower()))
        text_words = set(re.findall(r'\b[a-zA-Zà-ÿÀ-Ÿ]+\b', text.lower()))
        
        if not query_words:
            return 0
        
        overlap = len(query_words.intersection(text_words))
        return overlap / len(query_words)


class EnhancedRAGSystem:
    """Enhanced RAG system with advanced features"""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        persist_directory: str = "./chroma_db",
        use_reranking: bool = True
    ):
        self.chunker = TextChunker(chunk_size, chunk_overlap)
        # Use SimpleVectorStore for production (no chromadb dependency)
        self.vector_store = SimpleVectorStore() if not HAS_CHROMADB else ChromaVectorStore(persist_directory)
        self.reranker = ReRanker() if use_reranking else None
        self.document_hashes = set()
        self.document_metadata = {}
    
    def add_document(
        self,
        text: str,
        document_id: str = None,
        metadata: Dict = None
    ) -> int:
        """Add a document to the RAG system"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in self.document_hashes:
            return 0
        
        self.document_hashes.add(text_hash)
        
        if metadata:
            self.document_metadata[document_id] = metadata
        
        chunks = self.chunker.chunk_text(text, metadata)
        self.vector_store.add_documents(chunks, document_id)
        
        return len(chunks)
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_documents: List[str] = None,
        use_reranking: bool = True
    ) -> List[Dict]:
        """Search for relevant chunks"""
        initial_k = top_k * 3 if use_reranking and self.reranker else top_k
        results = self.vector_store.search(query, initial_k, filter_documents)
        
        if use_reranking and self.reranker and results:
            results = self.reranker.rerank(query, results, top_k)
        
        return results[:top_k]
    
    def get_relevant_context(
        self,
        query: str,
        top_k: int = 5,
        filter_documents: List[str] = None,
        include_metadata: bool = True
    ) -> str:
        """Get relevant context for a query"""
        results = self.search(query, top_k, filter_documents)
        
        if not results:
            return self.vector_store.get_all_text()[:5000]
        
        context_parts = []
        for result in results:
            text = result.get('text', '')
            
            if include_metadata:
                metadata = result.get('metadata', {})
                page = metadata.get('page_number', '')
                section = metadata.get('section_title', '')
                doc_id = metadata.get('document_id', result.get('document_id', ''))
                
                header = []
                if doc_id:
                    header.append(f"[Document: {doc_id}]")
                if page:
                    header.append(f"[Page: {page}]")
                if section:
                    header.append(f"[Section: {section}]")
                
                if header:
                    text = ' '.join(header) + '\n' + text
            
            context_parts.append(text)
        
        return '\n\n---\n\n'.join(context_parts)
    
    def get_full_context(self, document_ids: List[str] = None) -> str:
        """Get all document content, optionally filtered"""
        if document_ids:
            texts = []
            for doc_id in document_ids:
                texts.extend(self.vector_store.get_document_texts(doc_id))
            return '\n\n'.join(texts)
        return self.vector_store.get_all_text()
    
    def get_multi_document_context(
        self,
        query: str,
        document_ids: List[str],
        top_k_per_doc: int = 3
    ) -> Dict[str, List[Dict]]:
        """Get context from multiple documents for comparative questions"""
        results = {}
        for doc_id in document_ids:
            doc_results = self.search(query, top_k_per_doc, [doc_id])
            results[doc_id] = doc_results
        return results
    
    def clear(self):
        """Clear all documents"""
        self.vector_store.clear()
        self.document_hashes.clear()
        self.document_metadata.clear()
    
    def delete_document(self, document_id: str):
        """Delete a specific document"""
        self.vector_store.delete_document(document_id)
        if document_id in self.document_metadata:
            del self.document_metadata[document_id]
    
    def get_stats(self) -> Dict:
        """Get statistics about the stored documents"""
        stats = self.vector_store.get_stats()
        stats['unique_documents'] = len(self.document_hashes)
        stats['has_sentence_transformers'] = HAS_SENTENCE_TRANSFORMERS
        stats['has_chromadb'] = HAS_CHROMADB
        return stats


# Legacy compatibility classes
class SimpleVectorStore:
    """Legacy compatibility wrapper"""
    
    def __init__(self):
        self._store = ChromaVectorStore()
        self.documents = []
        self.doc_freqs = Counter()
        self.total_docs = 0
    
    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        words = re.findall(r'\b[a-zA-Zà-ÿÀ-Ÿ0-9]+\b', text)
        return [w for w in words if len(w) > 2]
    
    def _compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        tf = Counter(tokens)
        total = len(tokens)
        if total == 0:
            return {}
        return {term: count / total for term, count in tf.items()}
    
    def _compute_idf(self, term: str) -> float:
        if self.total_docs == 0:
            return 0
        df = self.doc_freqs.get(term, 0)
        if df == 0:
            return 0
        return math.log(self.total_docs / df)
    
    def add_documents(self, chunks: List[Dict], document_id: str = None):
        self._store.add_documents(chunks, document_id)
        for chunk in chunks:
            chunk['document_id'] = document_id
            tokens = self._tokenize(chunk['text'])
            chunk['tokens'] = tokens
            chunk['tf'] = self._compute_tf(tokens)
            unique_terms = set(tokens)
            for term in unique_terms:
                self.doc_freqs[term] += 1
            self.documents.append(chunk)
            self.total_docs += 1
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        return self._store.search(query, top_k)
    
    def get_all_text(self) -> str:
        return self._store.get_all_text()
    
    def clear(self):
        self._store.clear()
        self.documents = []
        self.doc_freqs = Counter()
        self.total_docs = 0


class RAGSystem:
    """Legacy compatibility wrapper"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self._rag = EnhancedRAGSystem(chunk_size, chunk_overlap)
        self.vector_store = SimpleVectorStore()
        self.chunker = self._rag.chunker
        self.document_hashes = self._rag.document_hashes
    
    def add_document(self, text: str, document_id: str = None) -> int:
        num_chunks = self._rag.add_document(text, document_id)
        self.vector_store._store = self._rag.vector_store
        return num_chunks
    
    def get_relevant_context(self, query: str, top_k: int = 5) -> str:
        return self._rag.get_relevant_context(query, top_k)
    
    def get_full_context(self) -> str:
        return self._rag.get_full_context()
    
    def clear(self):
        self._rag.clear()
        self.document_hashes = self._rag.document_hashes
    
    def get_stats(self) -> Dict:
        return self._rag.get_stats()
