#!/usr/bin/env python3
"""
BairdScienceQA CLI - Process science questions using Gemini 2.5 Flash via litellm
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bairdqa import load_questions, save_results
from llm import ask_llm

# Constants
DEFAULT_MODEL = 'gemini-2.5-flash'


def process_and_display(questions, subject, model=DEFAULT_MODEL):
    """Process questions and display results

    Args:
        questions: List of questions to process
        subject: Subject name
        model: LLM model to use

    Returns:
        List of results with questions and answers

    Raises:
        RuntimeError: If processing fails
    """
    results = []
    print(f"\n{'='*70}")
    print(f"Processing: {subject}")
    print(f"{'='*70}")

    for i, question in enumerate(questions, 1):
        try:
            print(f"\n[{i}/{len(questions)}] Q: {question}")
            answer = ask_llm(question, model)
            print(f"A: {answer}")
            results.append({"question": question, "answer": answer})
        except Exception as e:
            logger.error(f"Error processing question {i}: {e}")
            print(f"\n❌ Error: {str(e)}")
            raise RuntimeError(f"Failed to process question {i}: {str(e)}") from e

    return results


def get_questions_file():
    """Get path to questions.json file

    Returns:
        Path to questions file
    """
    base_dir = Path(__file__).parent.parent.parent
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
        print("\nEnter subject number to process (or 'all' for all subjects): ", end='')
        choice = input().strip()

        if choice.lower() == 'all':
            return 'all'

        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(subjects):
                print(f"❌ Invalid choice! Please enter 1-{len(subjects)} or 'all'")
                continue
            return subjects[idx]
        except ValueError:
            print(f"❌ Invalid choice! Please enter a number 1-{len(subjects)} or 'all'")
            continue


def main():
    """Main CLI application"""
    try:
        # Load questions
        questions_file = get_questions_file()
        logger.info(f"Loading questions from {questions_file}")
        questions_data = load_questions(questions_file)

        subjects = list(questions_data.keys())
        if not subjects:
            logger.error("No subjects found in questions file")
            print("❌ No subjects found in questions file")
            sys.exit(1)

        # Display available subjects
        print("\n" + "="*70)
        print("BairdScienceQA - CLI")
        print("="*70)
        print("\nAvailable subjects:")
        for i, subject in enumerate(subjects, 1):
            count = len(questions_data[subject])
            print(f"{i}. {subject} ({count} questions)")

        # Get subject choice
        choice = get_valid_subject(subjects)

        # Process subject(s)
        if choice == 'all':
            logger.info("Processing all subjects")
            all_results = {}
            failed_subjects = []
            for subject in subjects:
                try:
                    results = process_and_display(questions_data[subject], subject)
                    all_results[subject] = results
                    print(f"✅ Completed: {subject}")
                except Exception as e:
                    logger.error(f"Failed to process {subject}: {e}")
                    print(f"❌ Failed to process {subject}")
                    failed_subjects.append(subject)

            if all_results:
                output_file = 'all_answers.json'
                logger.info(f"Saving results to {output_file}")
                save_results(all_results, output_file)
                print(f"\n✅ Results saved to {output_file} ({len(all_results)}/{len(subjects)} subjects)")

            if failed_subjects:
                print(f"\n⚠️  Failed to process {len(failed_subjects)} subject(s): {', '.join(failed_subjects)}")
                sys.exit(1)

        else:
            logger.info(f"Processing subject: {choice}")
            try:
                results = process_and_display(questions_data[choice], choice)
                output_file = f"{choice.lower()}_answers.json"
                logger.info(f"Saving results to {output_file}")
                save_results(results, output_file)
                print(f"\n✅ Results saved to {output_file}")
            except Exception as e:
                logger.error(f"Failed to process {choice}: {e}")
                print(f"❌ Failed to process {choice}")
                sys.exit(1)

        print("\n" + "="*70)
        print("Processing complete!")
        print("="*70 + "\n")

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print(f"❌ {str(e)}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        print(f"❌ {str(e)}")
        sys.exit(1)
    except IOError as e:
        logger.error(f"IO error: {e}")
        print(f"❌ {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        print("\n\n❌ Processing interrupted")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
