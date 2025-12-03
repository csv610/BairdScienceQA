"""
LLM-related functions using litellm
"""

import logging
from litellm import completion

logger = logging.getLogger(__name__)


def ask_llm(question, model='gemini-2.5-flash'):
    """Ask LLM a question using litellm

    Args:
        question: The question to ask
        model: The model to use (default: gemini-2.5-flash)

    Returns:
        The response from the LLM

    Raises:
        ValueError: If question is empty
        RuntimeError: If LLM call fails
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    try:
        logger.debug(f"Asking {model}: {question[:50]}...")
        response = completion(
            model=model,
            messages=[{"role": "user", "content": question}],
            timeout=60
        )

        if not response or not response.choices:
            logger.error("Empty response from LLM")
            raise RuntimeError("LLM returned empty response")

        answer = response.choices[0].message.content
        if not answer:
            logger.error("Empty content in LLM response")
            raise RuntimeError("LLM returned empty content")

        logger.debug(f"Got response: {answer[:50]}...")
        return answer

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise
    except RuntimeError as e:
        logger.error(f"LLM error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error calling LLM: {type(e).__name__}: {e}")
        raise RuntimeError(f"Failed to get LLM response: {str(e)}") from e
