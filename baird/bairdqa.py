"""
Shared utilities for BairdScienceQA
"""

import json
import logging
from pathlib import Path
from .llm import ask_llm

logger = logging.getLogger(__name__)


def load_questions(file_path='questions.json'):
    """Load questions from JSON file

    Args:
        file_path: Path to questions JSON file

    Returns:
        Dictionary mapping subjects to list of questions

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not valid JSON or has invalid structure
    """
    try:
        path = Path(file_path)
        if not path.exists():
            logger.error(f"Questions file not found: {file_path}")
            raise FileNotFoundError(f"Questions file not found: {file_path}")

        with open(path, 'r') as f:
            data = json.load(f)

        if not isinstance(data, dict):
            logger.error("Questions data must be a dictionary")
            raise ValueError("Questions data must be a dictionary")

        if not data:
            logger.error("Questions data is empty")
            raise ValueError("Questions data is empty")

        for subject, questions in data.items():
            if not isinstance(questions, list):
                logger.error(f"Subject '{subject}' must have a list of questions")
                raise ValueError(f"Subject '{subject}' must have a list of questions")
            if not questions:
                logger.warning(f"Subject '{subject}' has no questions")

        logger.info(f"Loaded questions from {file_path}")
        return data

    except FileNotFoundError:
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        raise ValueError(f"Invalid JSON in {file_path}: {str(e)}") from e
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading questions: {e}")
        raise ValueError(f"Failed to load questions: {str(e)}") from e


def save_results(data, file_path):
    """Save results to JSON file

    Args:
        data: Data to save (dict or list)
        file_path: Path to save results to

    Raises:
        ValueError: If data is not JSON serializable
        IOError: If file cannot be written
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Results saved to {file_path}")

    except TypeError as e:
        logger.error(f"Data not JSON serializable: {e}")
        raise ValueError(f"Data not JSON serializable: {str(e)}") from e
    except IOError as e:
        logger.error(f"Cannot write to {file_path}: {e}")
        raise IOError(f"Cannot write to {file_path}: {str(e)}") from e
    except Exception as e:
        logger.error(f"Unexpected error saving results: {e}")
        raise IOError(f"Failed to save results: {str(e)}") from e


