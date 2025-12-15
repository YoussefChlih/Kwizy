# tests/test_routes.py
"""Tests for Flask application routes"""

import pytest
import os
import sys
import io
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestHomeRoutes:
    """Test home and basic routes"""
    
    def test_home_status(self, client):
        """Test that the home page returns 200"""
        resp = client.get("/")
        assert resp.status_code == 200
    
    def test_home_content_type(self, client):
        """Test that home page returns HTML"""
        resp = client.get("/")
        assert 'text/html' in resp.content_type


class TestHealthRoutes:
    """Test health check endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'healthy'


class TestDocumentRoutes:
    """Test document-related routes"""
    
    def test_get_documents_list(self, client):
        """Test that documents API returns success"""
        resp = client.get("/api/documents")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data.get('success') == True
        assert 'data' in data
    
    def test_clear_documents(self, client):
        """Test clearing documents"""
        resp = client.post("/api/documents/clear")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data.get('success') == True


class TestUploadRoutes:
    """Test file upload routes"""
    
    def test_upload_no_file(self, client):
        """Test upload without file returns error"""
        resp = client.post("/api/upload")
        assert resp.status_code == 400
        data = resp.get_json()
        assert data.get('success') == False
    
    def test_upload_empty_filename(self, client):
        """Test upload with empty filename"""
        data = {'file': (io.BytesIO(b''), '')}
        resp = client.post("/api/upload", data=data, content_type='multipart/form-data')
        assert resp.status_code == 400
    
    def test_upload_invalid_extension(self, client):
        """Test upload with invalid file extension"""
        data = {'file': (io.BytesIO(b'test content'), 'test.xyz')}
        resp = client.post("/api/upload", data=data, content_type='multipart/form-data')
        assert resp.status_code == 400
        result = resp.get_json()
        assert result.get('success') == False
        assert 'not allowed' in result.get('error', '').lower()
    
    def test_upload_valid_txt_file(self, client, app):
        """Test upload with valid text file"""
        test_content = b'This is test content for the quiz system. It has multiple sentences. Testing is important.'
        data = {'file': (io.BytesIO(test_content), 'test.txt')}
        resp = client.post("/api/upload", data=data, content_type='multipart/form-data')
        
        assert resp.status_code == 200
        result = resp.get_json()
        assert result.get('success') == True
        assert 'data' in result
        assert result['data']['filename'] == 'test.txt'


class TestQuizGenerationRoutes:
    """Test quiz generation routes"""
    
    def test_generate_without_documents_returns_error(self, client):
        """Test that generating quiz without documents returns error"""
        # Clear documents first
        client.post("/api/documents/clear")
        resp = client.post("/api/generate-quiz", json={})
        assert resp.status_code == 400
    
    def test_generate_without_documents_loaded(self, client):
        """Test generating quiz without any documents loaded"""
        # First clear any documents
        client.post("/api/documents/clear")
        
        resp = client.post("/api/generate-quiz", json={
            "num_questions": 5,
            "difficulty": "moyen",
            "question_types": ["comprehension"]
        })
        
        assert resp.status_code == 400
        data = resp.get_json()
        assert data.get('success') == False


class TestOptionsRoutes:
    """Test options endpoint"""
    
    def test_get_options(self, client):
        """Test getting quiz options"""
        resp = client.get("/api/options")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data.get('success') == True
        assert 'data' in data
        assert 'difficulties' in data['data']
        assert 'question_types' in data['data']


class TestSearchRoutes:
    """Test search routes"""
    
    def test_search_without_query(self, client):
        """Test search without query returns error"""
        resp = client.post("/api/search", json={})
        assert resp.status_code == 400
        data = resp.get_json()
        assert data.get('success') == False
    
    def test_search_with_query(self, client):
        """Test search with query"""
        # First upload a document
        test_content = b'Machine learning is a subset of artificial intelligence.'
        data = {'file': (io.BytesIO(test_content), 'test.txt')}
        client.post("/api/upload", data=data, content_type='multipart/form-data')
        
        # Then search
        resp = client.post("/api/search", json={"query": "machine learning"})
        assert resp.status_code == 200


class TestErrorHandlers:
    """Test error handlers"""
    
    def test_404_error(self, client):
        """Test 404 error handler"""
        resp = client.get("/nonexistent-route")
        assert resp.status_code == 404
        data = resp.get_json()
        assert data.get('success') == False


class TestStaticFiles:
    """Test static file serving"""
    
    def test_css_file(self, client):
        """Test CSS file is accessible"""
        resp = client.get("/static/css/style.css")
        assert resp.status_code == 200
    
    def test_js_file(self, client):
        """Test JS file is accessible"""
        resp = client.get("/static/js/app.js")
        assert resp.status_code == 200