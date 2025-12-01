"""
Shared utilities for BairdScienceQA
"""

import json
from litellm import completion


def load_questions(file_path='questions.json'):
    """Load questions from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)


def ask_llm(question, model='gemini-2.5-flash'):
    """Ask LLM a question using litellm"""
    response = completion(
        model=model,
        messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content


def save_results(data, file_path):
    """Save results to JSON file"""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def process_subject(questions_data, subject):
    """Process all questions for a subject and return results"""
    results = []
    questions = questions_data[subject]
    for i, question in enumerate(questions, 1):
        answer = ask_llm(question)
        results.append({"question": question, "answer": answer})
        yield i, len(questions), question, answer
    return results
