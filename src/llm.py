"""
LLM-related functions using litellm
"""

from litellm import completion


def ask_llm(question, model='gemini-2.5-flash'):
    """Ask LLM a question using litellm"""
    response = completion(
        model=model,
        messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content
