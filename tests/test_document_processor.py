# tests/test_document_processor.py
"""Tests for the DocumentProcessor module"""

import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from document_processor import DocumentProcessor, get_file_info


class TestDocumentProcessor:
    """Test class for DocumentProcessor"""
    
    @pytest.fixture
    def processor(self):
        """Create a DocumentProcessor instance"""
        return DocumentProcessor()
    
    @pytest.fixture
    def sample_txt_file(self, tmp_path):
        """Create a sample text file"""
        file_path = tmp_path / "sample.txt"
        file_path.write_text("Ceci est un fichier de test.\nIl contient plusieurs lignes.\nPour tester l'extraction.", encoding='utf-8')
        return str(file_path)
    
    def test_processor_initialization(self, processor):
        """Test that processor initializes correctly"""
        assert processor is not None
        assert len(processor.SUPPORTED_EXTENSIONS) > 0
        assert '.pdf' in processor.SUPPORTED_EXTENSIONS
        assert '.txt' in processor.SUPPORTED_EXTENSIONS
        assert '.docx' in processor.SUPPORTED_EXTENSIONS
    
    def test_supported_extensions(self, processor):
        """Test supported extensions list"""
        expected = {'.pdf', '.pptx', '.ppt', '.docx', '.doc', '.txt', '.rtf'}
        assert processor.SUPPORTED_EXTENSIONS == expected
    
    def test_process_txt_file(self, processor, sample_txt_file):
        """Test processing a text file"""
        text = processor.process(sample_txt_file)
        assert text is not None
        assert "fichier de test" in text
        assert "plusieurs lignes" in text
    
    def test_process_nonexistent_file(self, processor):
        """Test processing a non-existent file raises error"""
        with pytest.raises(FileNotFoundError):
            processor.process("nonexistent_file.txt")
    
    def test_process_unsupported_format(self, processor, tmp_path):
        """Test processing unsupported file format"""
        file_path = tmp_path / "test.xyz"
        file_path.write_text("test content")
        
        with pytest.raises(ValueError) as exc_info:
            processor.process(str(file_path))
        assert "Unsupported file format" in str(exc_info.value)
    
    def test_clean_text_method(self, processor):
        """Test the _clean_text method"""
        dirty_text = "  Multiple   spaces   and\n\n\nmultiple lines  "
        cleaned = processor._clean_text(dirty_text)
        assert "  " not in cleaned or cleaned.count("  ") < dirty_text.count("  ")
    
    def test_clean_text_empty(self, processor):
        """Test _clean_text with empty input"""
        assert processor._clean_text("") == ""
        assert processor._clean_text(None) == ""
    
    def test_table_to_text(self, processor):
        """Test _table_to_text method"""
        table = [
            ["Header1", "Header2"],
            ["Data1", "Data2"],
            ["Data3", "Data4"]
        ]
        result = processor._table_to_text(table)
        assert "Header1" in result
        assert "|" in result
    
    def test_table_to_text_empty(self, processor):
        """Test _table_to_text with empty table"""
        assert processor._table_to_text([]) == ""
        assert processor._table_to_text(None) == ""


class TestGetFileInfo:
    """Test class for get_file_info function"""
    
    def test_get_file_info(self, tmp_path):
        """Test getting file info"""
        file_path = tmp_path / "test.txt"
        file_path.write_text("test content")
        
        info = get_file_info(str(file_path))
        
        assert info is not None
        assert info['name'] == "test.txt"
        assert info['extension'] == ".txt"
        assert info['size'] > 0
    
    def test_get_file_info_nonexistent(self):
        """Test get_file_info with non-existent file"""
        result = get_file_info("nonexistent_file.txt")
        assert result is None


class TestDocumentProcessorEdgeCases:
    """Edge case tests for DocumentProcessor"""
    
    @pytest.fixture
    def processor(self):
        return DocumentProcessor()
    
    def test_empty_txt_file(self, processor, tmp_path):
        """Test processing empty text file"""
        file_path = tmp_path / "empty.txt"
        file_path.write_text("")
        
        text = processor.process(str(file_path))
        assert text == ""
    
    def test_unicode_content(self, processor, tmp_path):
        """Test processing file with unicode content"""
        file_path = tmp_path / "unicode.txt"
        content = "Café, résumé, naïve, señor, über, 日本語, العربية"
        file_path.write_text(content, encoding='utf-8')
        
        text = processor.process(str(file_path))
        assert "Café" in text
        assert "résumé" in text
    
    def test_large_text_file(self, processor, tmp_path):
        """Test processing a large text file"""
        file_path = tmp_path / "large.txt"
        content = "This is a test sentence. " * 10000
        file_path.write_text(content, encoding='utf-8')
        
        text = processor.process(str(file_path))
        assert len(text) > 0
        assert "test sentence" in text
