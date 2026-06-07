import sys
import os
import logging
import argparse
from pathlib import Path
from tqdm import tqdm

# Setup logging - log to file only
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('bairdqa.log')
    ]
)
logger = logging.getLogger(__name__)

# Suppress verbose logging from external libraries
logging.getLogger('litellm').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('litellm.utils').setLevel(logging.WARNING)
logging.getLogger('litellm.litellm_logging').setLevel(logging.WARNING)

# Disable LiteLLM's debug mode via environment
os.environ['LITELLM_LOG'] = 'None'

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import json

from baird.bairdqa import load_questions, save_results, save_results_markdown
from baird.llm import ask_llm

# Constants
DEFAULT_MODEL = 'ollama/gemma3'

def process_and_display(questions, subject, model=DEFAULT_MODEL, output_file=None, existing_results=None, progress_bar=None, all_results=None):
    """Process questions and display results, saving immediately to file after each question

    Args:
        questions: List of questions to process
        subject: Subject name
        model: LLM model to use
        output_file: Optional file path to save results immediately after each question
        existing_results: Existing results to check for already-answered questions
        progress_bar: Optional shared progress bar for all subjects
        all_results: Dict of all results organized by subject for immediate saving

    Returns:
        List of results with questions and answers

    Raises:
        RuntimeError: If processing fails
    """
    results = []
    existing_results = existing_results or {}
    all_results = all_results or {}

    for i, question in enumerate(questions, 1):
        try:
            # Check if answer already exists
            if question_answered_in_results(question, existing_results):
                logger.debug(f"Answer already exists for question: {question[:50]}...")
                # Find and reuse existing answer
                found = False
                if isinstance(existing_results, dict) and subject in existing_results:
                    for result in existing_results[subject]:
                        if result.get("question") == question:
                            answer = result.get("answer")
                            results.append({"question": question, "answer": answer})
                            found = True
                            break
                if not found:
                    for result in existing_results if isinstance(existing_results, list) else []:
                        if result.get("question") == question:
                            answer = result.get("answer")
                            results.append({"question": question, "answer": answer})
                            break
            else:
                # Query model for new answer
                answer = ask_llm(question, model)
                result_entry = {"question": question, "answer": answer}
                results.append(result_entry)

            # Save results immediately after each question if output_file provided
            if output_file:
                all_results[subject] = results
                save_results_markdown(all_results, output_file)

            # Update shared progress bar if provided
            if progress_bar:
                progress_bar.update(1)

        except Exception as e:
            logger.error(f"Error processing question {i}: {e}")
            raise RuntimeError(f"Failed to process question {i}: {str(e)}") from e

    return results


def sanitize_model_name(model):
    """Sanitize model name for use in filename

    Args:
        model: Model name (e.g., 'ollama/gemma3', 'gpt-4o')

    Returns:
        Sanitized model name suitable for filename
    """
    # Replace special characters with '_'
    return model.replace('/', '_').replace(':', '_').replace('-', '_').replace(' ', '_').lower()


def load_existing_results(output_file):
    """Load existing results from markdown output file

    Args:
        output_file: Path to the output file (expects .md extension)

    Returns:
        Dict of existing results, or empty dict if file doesn't exist
    """
    try:
        # Convert .json to .md if needed
        md_file = str(output_file).replace('.json', '.md')
        if Path(md_file).exists():
            from baird.bairdqa import load_markdown_results
            return load_markdown_results(md_file)
    except (IOError, ImportError) as e:
        logger.warning(f"Could not load existing results from {output_file}: {e}")
    return {}


def question_answered_in_results(question, results):
    """Check if a question is already answered in results

    Args:
        question: The question to check
        results: Results data (list or dict)

    Returns:
        True if question is answered, False otherwise
    """
    if isinstance(results, list):
        return any(r.get("question") == question for r in results)
    elif isinstance(results, dict):
        # For all subjects case, check all subject results
        for subject_results in results.values():
            if isinstance(subject_results, list):
                if any(r.get("question") == question for r in subject_results):
                    return True
    return False


def save_question_results(results, model):
    """Save question results to markdown file with model name

    Args:
        results: Question results to save (dict organized by subject)
        model: Model name used for answering
    """
    model_name = sanitize_model_name(model)
    output_file = f"baird_answers_{model_name}.md"
    logger.info(f"Saving results to {output_file}")
    save_results_markdown(results, output_file)


def get_questions_file():
    """Get path to questions.json file

    Returns:
        Path to questions file
    """
    base_dir = Path(__file__).parent.parent
    questions_file = base_dir / 'data' / 'questions.json'
    return str(questions_file)


def get_valid_subject(subjects):
    """Get validated subject choice from user

    Args:
        subjects: List of available subjects

    Returns:
        Selected subject name

    Raises:
        ValueError: If input is invalid
    """
    while True:
        choice = input().strip()

        if choice.lower() == 'all':
            return 'all'

        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(subjects):
                logger.warning(f"Invalid choice: {choice}")
                continue
            return subjects[idx]
        except ValueError:
            logger.warning(f"Invalid choice: {choice}")
            continue


def process_single_subject(questions_data, subject, model):
    """Process a single subject and save results immediately after each question

    Args:
        questions_data: Dict mapping subjects to questions
        subject: Subject to process
        model: Model to use

    Raises:
        RuntimeError: If processing fails
    """
    logger.info(f"Processing subject: {subject}")
    model_name = sanitize_model_name(model)
    output_file = f"baird_answers_{model_name}.md"
    logger.info(f"Saving results to {output_file}")

    # Load existing results to skip already-answered questions
    existing_results = load_existing_results(output_file)

    # Create progress bar for this subject
    total_questions = len(questions_data[subject])
    results_dict = {}
    with tqdm(total=total_questions, desc="Processing") as pbar:
        process_and_display(questions_data[subject], subject, model, output_file, existing_results, pbar, results_dict)


def process_all_subjects(questions_data, subjects, model):
    """Process all subjects and save results immediately after each question

    Args:
        questions_data: Dict mapping subjects to questions
        subjects: List of subjects to process
        model: Model to use

    Returns:
        True if all subjects processed successfully, False if any failed
    """
    logger.info("Processing all subjects")
    all_results = {}
    failed_subjects = []
    model_name = sanitize_model_name(model)
    output_file = f"baird_answers_{model_name}.md"
    logger.info(f"Saving results to {output_file}")

    # Load existing results to skip already-answered questions
    existing_results = load_existing_results(output_file)

    # Calculate total questions across all subjects
    total_questions = sum(len(questions_data[subject]) for subject in subjects)

    # Create single progress bar for all questions
    with tqdm(total=total_questions, desc="Processing") as pbar:
        for subject in subjects:
            try:
                process_and_display(questions_data[subject], subject, model, output_file, existing_results, pbar, all_results)
            except Exception as e:
                logger.error(f"Failed to process {subject}: {e}")
                failed_subjects.append(subject)

    if failed_subjects:
        logger.error(f"Failed to process {len(failed_subjects)} subject(s): {', '.join(failed_subjects)}")
        return False

    return True


def main():
    """Main CLI application"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="BairdScienceQA - Process science questions using an LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: python bairdqa_cli.py -m 'gpt-4o' or python bairdqa_cli.py --model 'claude-opus-4-5'"
    )
    parser.add_argument(
        '-m', '--model',
        type=str,
        default=DEFAULT_MODEL,
        help=f"Model to use for answering questions (default: {DEFAULT_MODEL})"
    )
    args = parser.parse_args()
    model = args.model

    try:
        # Load questions
        questions_file = get_questions_file()
        logger.info(f"Loading questions from {questions_file}")
        questions_data = load_questions(questions_file)

        subjects = list(questions_data.keys())
        if not subjects:
            logger.error("No subjects found in questions file")
            sys.exit(1)

        # Process all subjects automatically
        logger.info("Processing all subjects")
        logger.info(f"Using model: {model}")

        try:
            success = process_all_subjects(questions_data, subjects, model)
            if not success:
                sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to process: {e}")
            sys.exit(1)

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        sys.exit(1)
    except IOError as e:
        logger.error(f"IO error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
