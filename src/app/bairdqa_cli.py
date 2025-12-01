#!/usr/bin/env python3
"""
BairdScienceQA CLI - Process science questions using Gemini 2.5 Flash via litellm
"""

import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bairdqa import load_questions, ask_llm, save_results


def process_and_display(questions, subject, model='gemini-2.5-flash'):
    """Process questions and display results"""
    results = []
    print(f"\n{'='*70}")
    print(f"Processing: {subject}")
    print(f"{'='*70}")

    for i, question in enumerate(questions, 1):
        print(f"\n[{i}/{len(questions)}] Q: {question}")
        answer = ask_llm(question, model)
        print(f"A: {answer}")
        results.append({"question": question, "answer": answer})

    return results


def main():
    questions_data = load_questions('../data/questions.json')
    subjects = list(questions_data.keys())

    print("\nAvailable subjects:")
    for i, subject in enumerate(subjects, 1):
        print(f"{i}. {subject} ({len(questions_data[subject])} questions)")

    print("\nEnter subject number to process (or 'all' for all subjects): ", end='')
    choice = input().strip()

    if choice.lower() == 'all':
        all_results = {}
        for subject in subjects:
            results = process_and_display(questions_data[subject], subject)
            all_results[subject] = results

        save_results(all_results, 'all_answers.json')
        print(f"\n\nAll results saved to all_answers.json")
    else:
        try:
            idx = int(choice) - 1
            subject = subjects[idx]
        except (ValueError, IndexError):
            print("Invalid choice!")
            sys.exit(1)

        results = process_and_display(questions_data[subject], subject)
        output_file = f"{subject.lower()}_answers.json"
        save_results(results, output_file)
        print(f"\n\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
