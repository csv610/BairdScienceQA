"""
Shared utilities for BairdScienceQA
"""

import json
import logging
from pathlib import Path

try:
    from .llm import ask_llm
except ImportError:
    from llm import ask_llm

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

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

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


def format_results_as_markdown(results_dict):
    """Convert results dictionary to markdown format

    Args:
        results_dict: Dictionary mapping subjects to Q&A lists
                     {"Biology": [{"question": q, "answer": a}, ...], ...}

    Returns:
        String containing formatted markdown
    """
    markdown_lines = []

    for subject, qa_list in results_dict.items():
        # Subject header
        markdown_lines.append(f"# Subject: {subject}\n")

        for i, qa in enumerate(qa_list, 1):
            question = qa.get("question", "")
            answer = qa.get("answer", "")

            # Question header
            markdown_lines.append(f"## Question {i}")
            markdown_lines.append(question)
            markdown_lines.append("")

            # Answer header
            markdown_lines.append(f"## Answer {i}")
            markdown_lines.append(answer)
            markdown_lines.append("")

            # Separator
            markdown_lines.append("---")
            markdown_lines.append("")

        # Extra line between subjects
        markdown_lines.append("")

    return "\n".join(markdown_lines)


def save_results_markdown(data, file_path):
    """Save results to markdown file

    Args:
        data: Dictionary mapping subjects to Q&A lists
        file_path: Path to save markdown file to

    Raises:
        ValueError: If data structure is invalid
        IOError: If file cannot be written
    """
    try:
        # Validate data structure
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary organized by subject")

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to markdown format
        markdown_content = format_results_as_markdown(data)

        # Write to file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        logger.info(f"Results saved to {file_path}")

    except ValueError as e:
        logger.error(f"Invalid data structure: {e}")
        raise
    except IOError as e:
        logger.error(f"Cannot write to {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error saving markdown: {e}")
        raise IOError(f"Failed to save markdown: {str(e)}") from e


def parse_markdown_results(markdown_content):
    """Parse markdown content back to results dictionary

    Args:
        markdown_content: String containing markdown formatted results

    Returns:
        Dictionary mapping subjects to Q&A lists
    """
    results = {}
    current_subject = None
    current_question_lines = []
    current_answer_lines = []
    in_answer = False

    lines = markdown_content.split('\n')

    for line in lines:
        # Subject header
        if line.startswith('# Subject: '):
            # Save previous Q&A if exists
            if current_subject and current_question_lines and current_answer_lines:
                if current_subject not in results:
                    results[current_subject] = []
                results[current_subject].append({
                    "question": '\n'.join(current_question_lines).strip(),
                    "answer": '\n'.join(current_answer_lines).strip()
                })
                current_question_lines = []
                current_answer_lines = []

            current_subject = line[11:].strip()
            in_answer = False

        # Question header
        elif line.startswith('## Question '):
            # Save previous Q&A if exists
            if current_subject and current_question_lines and current_answer_lines:
                if current_subject not in results:
                    results[current_subject] = []
                results[current_subject].append({
                    "question": '\n'.join(current_question_lines).strip(),
                    "answer": '\n'.join(current_answer_lines).strip()
                })
                current_question_lines = []
                current_answer_lines = []

            in_answer = False

        # Answer header
        elif line.startswith('## Answer '):
            in_answer = True

        # Separator or empty line
        elif line.strip() in ['---', '']:
            continue

        # Content lines
        else:
            if in_answer:
                current_answer_lines.append(line)
            elif line.strip():
                current_question_lines.append(line)

    # Save last Q&A
    if current_subject and current_question_lines and current_answer_lines:
        if current_subject not in results:
            results[current_subject] = []
        results[current_subject].append({
            "question": '\n'.join(current_question_lines).strip(),
            "answer": '\n'.join(current_answer_lines).strip()
        })

    return results


def load_markdown_results(file_path):
    """Load results from markdown file

    Args:
        file_path: Path to markdown file

    Returns:
        Dictionary mapping subjects to Q&A lists
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return {}

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        return parse_markdown_results(content)

    except Exception as e:
        logger.warning(f"Could not load markdown results from {file_path}: {e}")
        return {}
