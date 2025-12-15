# tests/test_integration.py
"""Integration tests for the Quiz RAG System"""

import pytest
import os
import sys
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestFullWorkflow:
    """Integration tests for complete workflows"""
    
    def test_upload_and_get_documents(self, client):
        """Test uploading a document and then getting document info"""
        # Clear first
        client.post("/api/documents/clear")
        
        # Upload a document
        test_content = b'''
        Introduction to Machine Learning
        
        Machine learning is a branch of artificial intelligence that focuses on 
        building systems that can learn from and make decisions based on data.
        
        Key Concepts:
        1. Supervised Learning - Learning from labeled data
        2. Unsupervised Learning - Finding patterns in unlabeled data
        3. Reinforcement Learning - Learning through interaction
        
        Applications include image recognition, natural language processing, 
        and recommendation systems.
        '''
        
        data = {'file': (io.BytesIO(test_content), 'ml_intro.txt')}
        upload_resp = client.post("/api/upload", data=data, content_type='multipart/form-data')
        
        assert upload_resp.status_code == 200
        assert upload_resp.get_json()['success'] == True
        
        # Get document info
        doc_resp = client.get("/api/documents")
        assert doc_resp.status_code == 200
        doc_data = doc_resp.get_json()
        assert doc_data['data']['unique_documents'] >= 1
    
    def test_upload_search_workflow(self, client):
        """Test uploading and searching documents"""
        # Clear first
        client.post("/api/documents/clear")
        
        # Upload
        test_content = b'Python is a programming language. It is used for data science and web development.'
        data = {'file': (io.BytesIO(test_content), 'python.txt')}
        client.post("/api/upload", data=data, content_type='multipart/form-data')
        
        # Search
        search_resp = client.post("/api/search", json={"query": "programming language"})
        assert search_resp.status_code == 200
        assert search_resp.get_json()['success'] == True
    
    def test_clear_workflow(self, client):
        """Test clearing documents after upload"""
        # Upload something first
        test_content = b'Test content for clearing.'
        data = {'file': (io.BytesIO(test_content), 'test.txt')}
        client.post("/api/upload", data=data, content_type='multipart/form-data')
        
        # Clear
        clear_resp = client.post("/api/documents/clear")
        assert clear_resp.status_code == 200
        
        # Verify cleared
        doc_resp = client.get("/api/documents")
        doc_data = doc_resp.get_json()
        assert doc_data['data']['total_chunks'] == 0


class TestMultipleDocuments:
    """Test handling multiple documents"""
    
    def test_upload_multiple_documents(self, client):
        """Test uploading multiple documents"""
        client.post("/api/documents/clear")
        
        # Upload first document
        content1 = b'First document about artificial intelligence and machine learning.'
        data1 = {'file': (io.BytesIO(content1), 'doc1.txt')}
        resp1 = client.post("/api/upload", data=data1, content_type='multipart/form-data')
        assert resp1.status_code == 200
        
        # Upload second document
        content2 = b'Second document about Python programming and software development.'
        data2 = {'file': (io.BytesIO(content2), 'doc2.txt')}
        resp2 = client.post("/api/upload", data=data2, content_type='multipart/form-data')
        assert resp2.status_code == 200
        
        # Check both are stored
        doc_resp = client.get("/api/documents")
        doc_data = doc_resp.get_json()
        assert doc_data['data']['unique_documents'] >= 2


class TestAPIResponses:
    """Test API response formats"""
    
    def test_success_response_format(self, client):
        """Test successful responses have correct format"""
        resp = client.get("/api/health")
        data = resp.get_json()
        
        assert 'status' in data
        assert resp.content_type == 'application/json'
    
    def test_error_response_format(self, client):
        """Test error responses have correct format"""
        resp = client.post("/api/upload")  # No file
        data = resp.get_json()
        
        assert 'success' in data
        assert data['success'] == False
        assert 'error' in data
    
    def test_documents_response_format(self, client):
        """Test documents endpoint response format"""
        resp = client.get("/api/documents")
        data = resp.get_json()
        
        assert 'success' in data
        assert 'data' in data
        assert 'total_chunks' in data['data']
        assert 'unique_documents' in data['data']


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_large_file_content(self, client):
        """Test handling of larger text content"""
        client.post("/api/documents/clear")
        
        # Create larger content
        large_content = (b'This is a sentence about testing. ' * 1000)
        data = {'file': (io.BytesIO(large_content), 'large.txt')}
        
        resp = client.post("/api/upload", data=data, content_type='multipart/form-data')
        assert resp.status_code == 200
    
    def test_special_characters_in_content(self, client):
        """Test handling special characters"""
        client.post("/api/documents/clear")
        
        content = 'Test with special chars: é, è, ê, ë, à, â, ù, û, ô, î, ï, ç, €, £, ¥'.encode('utf-8')
        data = {'file': (io.BytesIO(content), 'special.txt')}
        
        resp = client.post("/api/upload", data=data, content_type='multipart/form-data')
        assert resp.status_code == 200
    
    def test_empty_search_results(self, client):
        """Test search with no matching results"""
        client.post("/api/documents/clear")
        
        # Upload something
        content = b'Content about cats and dogs.'
        data = {'file': (io.BytesIO(content), 'animals.txt')}
        client.post("/api/upload", data=data, content_type='multipart/form-data')
        
        # Search for something not in the document
        resp = client.post("/api/search", json={"query": "quantum physics"})
        assert resp.status_code == 200
