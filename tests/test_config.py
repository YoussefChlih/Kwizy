# tests/test_config.py
"""Tests for the Config module"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config


class TestConfig:
    """Test class for Config"""
    
    def test_config_has_secret_key(self):
        """Test that SECRET_KEY is defined"""
        assert hasattr(Config, 'SECRET_KEY')
        assert Config.SECRET_KEY is not None
    
    def test_config_has_upload_folder(self):
        """Test that UPLOAD_FOLDER is defined"""
        assert hasattr(Config, 'UPLOAD_FOLDER')
        assert Config.UPLOAD_FOLDER is not None
    
    def test_config_has_max_content_length(self):
        """Test that MAX_CONTENT_LENGTH is defined"""
        assert hasattr(Config, 'MAX_CONTENT_LENGTH')
        assert Config.MAX_CONTENT_LENGTH > 0
    
    def test_config_has_allowed_extensions(self):
        """Test that ALLOWED_EXTENSIONS is defined"""
        assert hasattr(Config, 'ALLOWED_EXTENSIONS')
        assert isinstance(Config.ALLOWED_EXTENSIONS, set)
        assert len(Config.ALLOWED_EXTENSIONS) > 0
    
    def test_allowed_extensions_contains_pdf(self):
        """Test that PDF is in allowed extensions"""
        assert 'pdf' in Config.ALLOWED_EXTENSIONS
    
    def test_allowed_extensions_contains_docx(self):
        """Test that DOCX is in allowed extensions"""
        assert 'docx' in Config.ALLOWED_EXTENSIONS
    
    def test_allowed_extensions_contains_txt(self):
        """Test that TXT is in allowed extensions"""
        assert 'txt' in Config.ALLOWED_EXTENSIONS
    
    def test_allowed_extensions_contains_pptx(self):
        """Test that PPTX is in allowed extensions"""
        assert 'pptx' in Config.ALLOWED_EXTENSIONS


class TestRAGSettings:
    """Test RAG-related configuration"""
    
    def test_chunk_size(self):
        """Test CHUNK_SIZE is reasonable"""
        assert hasattr(Config, 'CHUNK_SIZE')
        assert Config.CHUNK_SIZE > 0
        assert Config.CHUNK_SIZE <= 10000
    
    def test_chunk_overlap(self):
        """Test CHUNK_OVERLAP is reasonable"""
        assert hasattr(Config, 'CHUNK_OVERLAP')
        assert Config.CHUNK_OVERLAP >= 0
        assert Config.CHUNK_OVERLAP < Config.CHUNK_SIZE
    
    def test_top_k_results(self):
        """Test TOP_K_RESULTS is reasonable"""
        assert hasattr(Config, 'TOP_K_RESULTS')
        assert Config.TOP_K_RESULTS > 0


class TestQuizSettings:
    """Test Quiz-related configuration"""
    
    def test_difficulty_levels_exist(self):
        """Test that difficulty levels are defined"""
        assert hasattr(Config, 'DIFFICULTY_LEVELS')
        assert isinstance(Config.DIFFICULTY_LEVELS, dict)
    
    def test_difficulty_levels_content(self):
        """Test difficulty levels contain expected keys"""
        assert 'facile' in Config.DIFFICULTY_LEVELS
        assert 'moyen' in Config.DIFFICULTY_LEVELS
        assert 'difficile' in Config.DIFFICULTY_LEVELS
    
    def test_question_types_exist(self):
        """Test that question types are defined"""
        assert hasattr(Config, 'QUESTION_TYPES')
        assert isinstance(Config.QUESTION_TYPES, dict)
    
    def test_question_types_content(self):
        """Test question types contain expected keys"""
        assert 'comprehension' in Config.QUESTION_TYPES
        assert 'memorisation' in Config.QUESTION_TYPES
        assert 'qcm' in Config.QUESTION_TYPES
        assert 'vrai_faux' in Config.QUESTION_TYPES
        assert 'reponse_courte' in Config.QUESTION_TYPES
