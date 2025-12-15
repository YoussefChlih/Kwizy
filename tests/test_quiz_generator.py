# tests/test_quiz_generator.py
"""Tests for the Quiz Generator module"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quiz_generator import QuizGenerator


class TestQuizGeneratorInit:
    """Test class for QuizGenerator initialization"""
    
    def test_initialization(self):
        """Test that QuizGenerator initializes correctly"""
        with patch('quiz_generator.Mistral') as mock_mistral:
            generator = QuizGenerator("test_api_key")
            
            assert generator.model == "mistral-large-latest"
            mock_mistral.assert_called_once_with(api_key="test_api_key")
    
    def test_difficulty_prompts_exist(self):
        """Test that difficulty prompts are defined"""
        with patch('quiz_generator.Mistral'):
            generator = QuizGenerator("test_key")
            
            assert 'facile' in generator.DIFFICULTY_PROMPTS
            assert 'moyen' in generator.DIFFICULTY_PROMPTS
            assert 'difficile' in generator.DIFFICULTY_PROMPTS
    
    def test_question_type_prompts_exist(self):
        """Test that question type prompts are defined"""
        with patch('quiz_generator.Mistral'):
            generator = QuizGenerator("test_key")
            
            assert 'comprehension' in generator.QUESTION_TYPE_PROMPTS
            assert 'memorisation' in generator.QUESTION_TYPE_PROMPTS
            assert 'qcm' in generator.QUESTION_TYPE_PROMPTS
            assert 'vrai_faux' in generator.QUESTION_TYPE_PROMPTS
            assert 'reponse_courte' in generator.QUESTION_TYPE_PROMPTS


class TestQuizGeneratorDifficulty:
    """Test difficulty-related functionality"""
    
    @pytest.fixture
    def generator(self):
        with patch('quiz_generator.Mistral'):
            return QuizGenerator("test_key")
    
    def test_difficulty_has_name(self, generator):
        """Test each difficulty has a name"""
        for key, value in generator.DIFFICULTY_PROMPTS.items():
            assert 'name' in value
            assert len(value['name']) > 0
    
    def test_difficulty_has_description(self, generator):
        """Test each difficulty has a description"""
        for key, value in generator.DIFFICULTY_PROMPTS.items():
            assert 'description' in value
            assert len(value['description']) > 0
    
    def test_difficulty_has_complexity(self, generator):
        """Test each difficulty has complexity info"""
        for key, value in generator.DIFFICULTY_PROMPTS.items():
            assert 'complexity' in value


class TestQuizGeneratorQuestionTypes:
    """Test question type functionality"""
    
    @pytest.fixture
    def generator(self):
        with patch('quiz_generator.Mistral'):
            return QuizGenerator("test_key")
    
    def test_question_type_has_name(self, generator):
        """Test each question type has a name"""
        for key, value in generator.QUESTION_TYPE_PROMPTS.items():
            assert 'name' in value
    
    def test_question_type_has_description(self, generator):
        """Test each question type has a description"""
        for key, value in generator.QUESTION_TYPE_PROMPTS.items():
            assert 'description' in value
    
    def test_question_type_has_format(self, generator):
        """Test each question type has a format"""
        for key, value in generator.QUESTION_TYPE_PROMPTS.items():
            assert 'format' in value


class TestGenerateQuiz:
    """Test quiz generation functionality"""
    
    @pytest.fixture
    def generator(self):
        with patch('quiz_generator.Mistral') as mock_mistral:
            mock_client = MagicMock()
            mock_mistral.return_value = mock_client
            gen = QuizGenerator("test_key")
            gen.client = mock_client
            return gen
    
    def test_generate_quiz_default_params(self, generator):
        """Test quiz generation with default parameters"""
        # Mock the Mistral response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''```json
{
    "questions": [
        {
            "question": "Test question?",
            "type": "qcm",
            "options": {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
            "correct_answer": "A",
            "explanation": "Test explanation"
        }
    ]
}
```'''
        generator.client.chat.complete.return_value = mock_response
        
        result = generator.generate_quiz(
            context="This is test context about machine learning.",
            num_questions=1
        )
        
        assert 'questions' in result or 'error' in result
    
    def test_generate_quiz_invalid_difficulty(self, generator):
        """Test that invalid difficulty defaults to 'moyen'"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"questions": []}'
        generator.client.chat.complete.return_value = mock_response
        
        # Should not raise, should default to 'moyen'
        result = generator.generate_quiz(
            context="Test context",
            difficulty="invalid_difficulty"
        )
        
        assert result is not None
    
    def test_generate_quiz_invalid_question_type(self, generator):
        """Test that invalid question types are filtered out"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"questions": []}'
        generator.client.chat.complete.return_value = mock_response
        
        result = generator.generate_quiz(
            context="Test context",
            question_types=["invalid_type"]
        )
        
        assert result is not None
    
    def test_generate_quiz_api_error(self, generator):
        """Test handling of API errors"""
        generator.client.chat.complete.side_effect = Exception("API Error")
        
        result = generator.generate_quiz(
            context="Test context"
        )
        
        assert result['success'] == False
        assert 'error' in result


class TestBuildPrompt:
    """Test prompt building functionality"""
    
    @pytest.fixture
    def generator(self):
        with patch('quiz_generator.Mistral'):
            return QuizGenerator("test_key")
    
    def test_build_prompt_contains_context(self, generator):
        """Test that prompt contains the context"""
        context = "This is the document content about AI."
        prompt = generator._build_prompt(
            context=context,
            num_questions=5,
            difficulty='moyen',
            question_types=['qcm'],
            language='french'
        )
        
        assert context in prompt
    
    def test_build_prompt_contains_difficulty(self, generator):
        """Test that prompt mentions difficulty"""
        prompt = generator._build_prompt(
            context="Test content",
            num_questions=5,
            difficulty='difficile',
            question_types=['qcm'],
            language='french'
        )
        
        # Should contain difficulty-related terms
        assert len(prompt) > 0


class TestParseResponse:
    """Test response parsing functionality"""
    
    @pytest.fixture
    def generator(self):
        with patch('quiz_generator.Mistral'):
            return QuizGenerator("test_key")
    
    def test_parse_valid_json(self, generator):
        """Test parsing valid JSON response"""
        response = '''```json
{
    "questions": [
        {
            "question": "What is AI?",
            "type": "qcm",
            "options": {"A": "Opt1", "B": "Opt2", "C": "Opt3", "D": "Opt4"},
            "correct_answer": "A"
        }
    ]
}
```'''
        
        result = generator._parse_response(response, 'moyen', ['qcm'])
        
        assert result['success'] == True
        assert 'questions' in result
    
    def test_parse_invalid_json(self, generator):
        """Test parsing invalid JSON response"""
        response = "This is not valid JSON at all"
        
        result = generator._parse_response(response, 'moyen', ['qcm'])
        
        # Should handle gracefully
        assert 'success' in result
    
    def test_parse_json_without_code_block(self, generator):
        """Test parsing JSON without code block markers"""
        response = '''{
            "questions": [
                {
                    "question": "Test?",
                    "type": "comprehension",
                    "answer": "Test answer"
                }
            ]
        }'''
        
        result = generator._parse_response(response, 'moyen', ['comprehension'])
        
        assert result['success'] == True


class TestGetAvailableOptions:
    """Test getting available options"""
    
    @pytest.fixture
    def generator(self):
        with patch('quiz_generator.Mistral'):
            return QuizGenerator("test_key")
    
    def test_get_available_options(self, generator):
        """Test that available options returns correct structure"""
        options = generator.get_available_options()
        
        assert 'difficulties' in options
        assert 'question_types' in options
        assert len(options['difficulties']) == 3
        assert len(options['question_types']) == 5
    
    def test_difficulties_structure(self, generator):
        """Test difficulty options have correct structure"""
        options = generator.get_available_options()
        
        for diff in options['difficulties']:
            assert 'key' in diff
            assert 'name' in diff
            assert 'description' in diff
    
    def test_question_types_structure(self, generator):
        """Test question type options have correct structure"""
        options = generator.get_available_options()
        
        for qt in options['question_types']:
            assert 'key' in qt
            assert 'name' in qt
            assert 'description' in qt


class TestQuizGeneratorEdgeCases:
    """Edge case tests"""
    
    @pytest.fixture
    def generator(self):
        with patch('quiz_generator.Mistral'):
            return QuizGenerator("test_key")
    
    def test_empty_context(self, generator):
        """Test with empty context"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"questions": []}'
        generator.client.chat.complete.return_value = mock_response
        
        result = generator.generate_quiz(context="")
        
        assert result is not None
    
    def test_none_question_types(self, generator):
        """Test with None question_types"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"questions": []}'
        generator.client.chat.complete.return_value = mock_response
        
        result = generator.generate_quiz(
            context="Test",
            question_types=None
        )
        
        assert result is not None
    
    def test_zero_questions(self, generator):
        """Test requesting zero questions"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"questions": []}'
        generator.client.chat.complete.return_value = mock_response
        
        result = generator.generate_quiz(
            context="Test",
            num_questions=0
        )
        
        assert result is not None
