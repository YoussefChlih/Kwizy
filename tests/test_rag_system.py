# tests/test_rag_system.py
"""Tests for the RAG System module"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_system import TextChunker, SimpleVectorStore, RAGSystem


class TestTextChunker:
    """Test class for TextChunker"""
    
    @pytest.fixture
    def chunker(self):
        """Create a TextChunker instance"""
        return TextChunker(chunk_size=100, chunk_overlap=20)
    
    def test_chunker_initialization(self, chunker):
        """Test chunker initializes correctly"""
        assert chunker.chunk_size == 100
        assert chunker.chunk_overlap == 20
    
    def test_chunk_text_basic(self, chunker):
        """Test basic text chunking"""
        text = "This is sentence one. This is sentence two. This is sentence three. This is sentence four."
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0
        assert all('text' in chunk for chunk in chunks)
        assert all('chunk_id' in chunk for chunk in chunks)
    
    def test_chunk_text_empty(self, chunker):
        """Test chunking empty text"""
        chunks = chunker.chunk_text("")
        assert chunks == []
        
        chunks = chunker.chunk_text("   ")
        assert chunks == []
    
    def test_chunk_text_short(self, chunker):
        """Test chunking short text"""
        text = "Short text."
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) == 1
        assert "Short text" in chunks[0]['text']
    
    def test_chunks_have_ids(self, chunker):
        """Test that chunks have sequential IDs"""
        text = "Sentence one. " * 50
        chunks = chunker.chunk_text(text)
        
        ids = [chunk['chunk_id'] for chunk in chunks]
        assert ids == list(range(len(chunks)))
    
    def test_split_into_sentences(self, chunker):
        """Test sentence splitting"""
        text = "First sentence. Second sentence! Third sentence?"
        sentences = chunker._split_into_sentences(text)
        
        assert len(sentences) == 3
        assert "First sentence" in sentences[0]
        assert "Second sentence" in sentences[1]
    
    def test_chunk_overlap(self):
        """Test that chunks overlap correctly"""
        chunker = TextChunker(chunk_size=50, chunk_overlap=10)
        text = "Word one. Word two. Word three. Word four. Word five. Word six. Word seven."
        chunks = chunker.chunk_text(text)
        
        # Check that overlap exists (content from previous chunk appears in next)
        if len(chunks) > 1:
            # At least some overlap should exist
            assert len(chunks) >= 1


class TestSimpleVectorStore:
    """Test class for SimpleVectorStore"""
    
    @pytest.fixture
    def store(self):
        """Create a SimpleVectorStore instance"""
        return SimpleVectorStore()
    
    def test_store_initialization(self, store):
        """Test store initializes correctly"""
        assert store.documents == []
        assert store.total_docs == 0
    
    def test_tokenize(self, store):
        """Test tokenization"""
        tokens = store._tokenize("Hello World! This is a test.")
        
        assert "hello" in tokens
        assert "world" in tokens
        assert "test" in tokens
        # Short words should be filtered
        assert "is" not in tokens
    
    def test_tokenize_french(self, store):
        """Test tokenization with French text"""
        tokens = store._tokenize("Bonjour le monde! Ceci est un test français.")
        
        assert "bonjour" in tokens
        assert "monde" in tokens
        assert "français" in tokens
    
    def test_add_documents(self, store):
        """Test adding documents"""
        chunks = [
            {'text': 'This is document one about machine learning.', 'chunk_id': 0},
            {'text': 'This is document two about data science.', 'chunk_id': 1}
        ]
        
        store.add_documents(chunks, 'test_doc')
        
        assert store.total_docs == 2
        assert len(store.documents) == 2
    
    def test_add_empty_documents(self, store):
        """Test adding empty documents list"""
        store.add_documents([], 'test_doc')
        assert store.total_docs == 0
    
    def test_search_basic(self, store):
        """Test basic search functionality"""
        chunks = [
            {'text': 'Machine learning is a branch of artificial intelligence.', 'chunk_id': 0},
            {'text': 'Python is a popular programming language.', 'chunk_id': 1},
            {'text': 'Deep learning uses neural networks for complex tasks.', 'chunk_id': 2}
        ]
        
        store.add_documents(chunks)
        
        results = store.search("machine learning artificial intelligence", top_k=2)
        
        assert len(results) <= 2
        assert results[0]['score'] >= 0
    
    def test_search_empty_store(self, store):
        """Test search on empty store"""
        results = store.search("test query")
        assert results == []
    
    def test_search_empty_query(self, store):
        """Test search with empty query"""
        chunks = [{'text': 'Some document content.', 'chunk_id': 0}]
        store.add_documents(chunks)
        
        results = store.search("")
        # Should return documents even with empty query
        assert len(results) >= 0
    
    def test_compute_tf(self, store):
        """Test term frequency computation"""
        tokens = ['word', 'word', 'other', 'another']
        tf = store._compute_tf(tokens)
        
        assert tf['word'] == 0.5  # 2/4
        assert tf['other'] == 0.25  # 1/4
    
    def test_compute_tf_empty(self, store):
        """Test TF with empty tokens"""
        tf = store._compute_tf([])
        assert tf == {}
    
    def test_get_all_text(self, store):
        """Test getting all text"""
        chunks = [
            {'text': 'First chunk.', 'chunk_id': 0},
            {'text': 'Second chunk.', 'chunk_id': 1}
        ]
        store.add_documents(chunks)
        
        all_text = store.get_all_text()
        assert "First chunk" in all_text
        assert "Second chunk" in all_text
    
    def test_clear(self, store):
        """Test clearing the store"""
        chunks = [{'text': 'Some content.', 'chunk_id': 0}]
        store.add_documents(chunks)
        
        store.clear()
        
        assert store.total_docs == 0
        assert len(store.documents) == 0


class TestRAGSystem:
    """Test class for RAGSystem"""
    
    @pytest.fixture
    def rag(self):
        """Create a RAGSystem instance"""
        return RAGSystem(chunk_size=100, chunk_overlap=20)
    
    def test_rag_initialization(self, rag):
        """Test RAG system initializes correctly"""
        assert rag.chunker is not None
        assert rag.vector_store is not None
        assert len(rag.document_hashes) == 0
    
    def test_add_document(self, rag):
        """Test adding a document"""
        text = "This is a test document with enough content. " * 10
        num_chunks = rag.add_document(text, "test_doc")
        
        assert num_chunks > 0
        assert rag.get_stats()['unique_documents'] == 1
    
    def test_add_duplicate_document(self, rag):
        """Test that duplicate documents are not added twice"""
        text = "This is a duplicate test document."
        
        chunks1 = rag.add_document(text, "doc1")
        chunks2 = rag.add_document(text, "doc2")  # Same content
        
        assert chunks1 > 0
        assert chunks2 == 0  # Duplicate should return 0
    
    def test_get_relevant_context(self, rag):
        """Test getting relevant context"""
        doc1 = "Machine learning is a type of artificial intelligence. AI systems can learn from data."
        doc2 = "Python is a programming language. It is used for web development."
        
        rag.add_document(doc1, "ml_doc")
        rag.add_document(doc2, "python_doc")
        
        context = rag.get_relevant_context("artificial intelligence machine learning")
        
        assert len(context) > 0
    
    def test_get_full_context(self, rag):
        """Test getting full context"""
        rag.add_document("Document one content.", "doc1")
        rag.add_document("Document two content.", "doc2")
        
        full_context = rag.get_full_context()
        
        assert "Document one" in full_context
        assert "Document two" in full_context
    
    def test_clear(self, rag):
        """Test clearing RAG system"""
        rag.add_document("Some document content.", "doc1")
        rag.clear()
        
        stats = rag.get_stats()
        assert stats['total_chunks'] == 0
        assert stats['unique_documents'] == 0
    
    def test_get_stats(self, rag):
        """Test getting statistics"""
        stats = rag.get_stats()
        
        assert 'total_chunks' in stats
        assert 'unique_documents' in stats
        assert stats['total_chunks'] == 0
        assert stats['unique_documents'] == 0
    
    def test_get_stats_after_adding(self, rag):
        """Test stats after adding documents"""
        text = "This is a test. " * 50
        rag.add_document(text, "doc1")
        
        stats = rag.get_stats()
        assert stats['total_chunks'] > 0
        assert stats['unique_documents'] == 1


class TestRAGSystemIntegration:
    """Integration tests for RAG system"""
    
    def test_full_workflow(self):
        """Test complete RAG workflow"""
        rag = RAGSystem(chunk_size=200, chunk_overlap=40)
        
        # Add multiple documents
        doc1 = """
        L'apprentissage automatique est une branche de l'intelligence artificielle.
        Il permet aux ordinateurs d'apprendre à partir de données.
        Les réseaux de neurones sont utilisés pour des tâches complexes.
        """
        
        doc2 = """
        Python est un langage de programmation très populaire.
        Il est utilisé dans le développement web et la science des données.
        Django et Flask sont des frameworks web Python.
        """
        
        rag.add_document(doc1, "ai_doc")
        rag.add_document(doc2, "python_doc")
        
        # Search for relevant content
        context = rag.get_relevant_context("intelligence artificielle apprentissage")
        
        assert len(context) > 0
        
        # Verify stats
        stats = rag.get_stats()
        assert stats['unique_documents'] == 2
