import json
import pytest
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from bairdqa import load_questions


@pytest.fixture
def sample_questions():
    return {
        "Biology": [
            "What makes us human?",
            "How did life begin?",
            "What is DNA?"
        ],
        "Physics": [
            "What is gravity?",
            "What is time?",
            "What is light?"
        ]
    }


@pytest.fixture
def temp_questions_file(sample_questions):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_questions, f)
        return f.name


def test_load_questions(temp_questions_file, sample_questions):
    """Test loading questions from JSON file"""
    questions = load_questions(temp_questions_file)
    assert questions == sample_questions
    assert "Biology" in questions
    assert "Physics" in questions


def test_load_questions_file_not_found():
    """Test error handling when questions file not found"""
    with pytest.raises(FileNotFoundError):
        load_questions("nonexistent_file.json")


def test_biology_questions_count(sample_questions):
    """Test Biology subject has correct number of questions"""
    assert len(sample_questions["Biology"]) == 3


def test_physics_questions_count(sample_questions):
    """Test Physics subject has correct number of questions"""
    assert len(sample_questions["Physics"]) == 3


def test_question_content(sample_questions):
    """Test that questions are strings"""
    for subject, questions in sample_questions.items():
        for question in questions:
            assert isinstance(question, str)
            assert len(question) > 0
