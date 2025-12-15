# tests/conftest.py
"""Pytest configuration and fixtures"""

import sys
import os
import pytest
import tempfile
import shutil

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app


@pytest.fixture(scope='function')
def app():
    """Create Flask app instance for testing"""
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    
    # Use a temporary upload folder for tests
    temp_upload = tempfile.mkdtemp()
    flask_app.config['UPLOAD_FOLDER'] = temp_upload
    os.makedirs(temp_upload, exist_ok=True)
    
    yield flask_app
    
    # Cleanup
    if os.path.exists(temp_upload):
        shutil.rmtree(temp_upload)


@pytest.fixture(scope='function')
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def sample_text_content():
    """Sample text content for testing"""
    return """
    Introduction à l'Intelligence Artificielle
    
    L'intelligence artificielle (IA) est un domaine de l'informatique qui vise à créer
    des machines capables de simuler l'intelligence humaine.
    
    Types d'IA:
    1. IA Faible - Systèmes spécialisés dans une tâche
    2. IA Forte - Systèmes capables de raisonnement général
    
    Applications:
    - Reconnaissance vocale
    - Traitement du langage naturel
    - Vision par ordinateur
    - Systèmes de recommandation
    """


@pytest.fixture
def sample_pdf_content():
    """Sample content that simulates PDF extraction"""
    return """
    --- Page 1 ---
    Chapitre 1: Introduction
    
    Ce document présente les concepts fondamentaux de l'apprentissage automatique.
    
    --- Page 2 ---
    Chapitre 2: Algorithmes
    
    Les algorithmes d'apprentissage supervisé incluent la régression et la classification.
    """