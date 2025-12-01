import random
import os
import sys
import logging
from pathlib import Path

from gtts import gTTS
import vlc
import streamlit as st

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bairdqa import load_questions as load_questions_util
from llm import ask_llm

# Constants
MODELS = ['gemini-2.5-flash', 'gpt-4', 'claude-3-sonnet']
DEFAULT_MODEL = MODELS[0]
AUDIO_FILE = 'answer.mp3'


@st.cache_data
def load_questions():
    """Load questions from data directory"""
    base_dir = Path(__file__).parent.parent.parent
    questions_path = base_dir / 'data' / 'questions.json'
    return load_questions_util(str(questions_path))


def initialize_session_state():
    """Initialize all session state variables"""
    if 'question' not in st.session_state:
        st.session_state.question = None
    if 'answer' not in st.session_state:
        st.session_state.answer = None
    if 'subject' not in st.session_state:
        st.session_state.subject = None
    if 'remaining_questions' not in st.session_state:
        st.session_state.remaining_questions = None


def generate_new_question(questions):
    """Generate a new question from the remaining questions.

    Args:
        questions: List of all questions for the subject

    Returns:
        A new question or None if no questions remain
    """
    if not st.session_state.remaining_questions:
        return None

    if not st.session_state.remaining_questions:
        return None

    random_index = random.choice(list(st.session_state.remaining_questions))
    selected_question = questions[random_index]
    st.session_state.remaining_questions.remove(random_index)

    return selected_question


def text_to_speech(text):
    """Convert text to speech and play it using VLC.

    Args:
        text: Text to convert to speech

    Raises:
        ValueError: If text is empty
        RuntimeError: If audio generation or playback fails
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    try:
        logger.info("Generating speech...")
        tts = gTTS(text=text, lang='en')
        tts.save(AUDIO_FILE)
        logger.info(f"Speech saved to {AUDIO_FILE}")

        logger.info("Playing audio...")
        player = vlc.MediaPlayer(AUDIO_FILE)
        player.play()

    except FileNotFoundError as e:
        logger.error(f"Audio file not found: {e}")
        raise RuntimeError(f"Failed to save audio: {str(e)}") from e
    except Exception as e:
        logger.error(f"Error in text-to-speech: {e}")
        raise RuntimeError(f"Failed to play audio: {str(e)}") from e


def reset_questions():
    """Reset the question and answer in session state."""
    st.session_state.question = None
    st.session_state.answer = None
    st.session_state.remaining_questions = None


def main():
    """Main Streamlit application"""
    initialize_session_state()

    st.set_page_config(page_title="BairdScienceQA", layout="wide")
    st.title("Science Q&A with LLM")

    # Sidebar controls
    with st.sidebar:
        st.title("Controls")

        # Model selection
        model_name = st.selectbox(
            'Select a model',
            MODELS,
            index=MODELS.index(DEFAULT_MODEL),
            help="Choose the LLM model to use"
        )

        # Load questions
        try:
            questions_data = load_questions()
        except Exception as e:
            st.error(f"Failed to load questions: {str(e)}")
            logger.error(f"Error loading questions: {e}")
            return

        subjects = list(questions_data.keys())
        if not subjects:
            st.error("No subjects found in questions file")
            return

        # Subject selection
        if st.session_state.subject not in subjects:
            st.session_state.subject = subjects[0]

        subject = st.selectbox(
            "Choose a subject",
            subjects,
            index=subjects.index(st.session_state.subject),
            on_change=reset_questions,
            help="Select a science subject"
        )

        if subject != st.session_state.subject:
            st.session_state.subject = subject
            reset_questions()

        questions = questions_data[subject]
        st.write(f"**Total questions:** {len(questions)}")

        # Initialize remaining questions if needed
        if st.session_state.remaining_questions is None:
            st.session_state.remaining_questions = set(range(len(questions)))

        remaining_count = len(st.session_state.remaining_questions)
        st.write(f"**Remaining:** {remaining_count}")

        # New question button
        if st.button("🆕 New Question", use_container_width=True):
            st.session_state.question = generate_new_question(questions)
            if st.session_state.question:
                st.session_state.answer = None
            else:
                st.warning("No more questions available!")

    # Main content area
    if st.session_state.question is None:
        st.info("Click 'New Question' to get started!")
    else:
        # Display question
        st.subheader("Question")
        st.write(st.session_state.question)

        # Ask LLM button
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🤖 Ask LLM", use_container_width=True):
                try:
                    with st.spinner("Generating answer..."):
                        st.session_state.answer = ask_llm(
                            st.session_state.question,
                            model_name
                        )
                    st.success("Got answer!")
                except ValueError as e:
                    st.error(f"Invalid input: {str(e)}")
                    logger.error(f"Validation error: {e}")
                except RuntimeError as e:
                    st.error(f"LLM error: {str(e)}")
                    logger.error(f"LLM error: {e}")
                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")
                    logger.error(f"Unexpected error: {e}")

        # Display answer if available
        if st.session_state.answer is not None:
            st.subheader("Answer")
            st.write(st.session_state.answer)

            with col2:
                if st.button("🔊 Speak Answer", use_container_width=True):
                    try:
                        with st.spinner("Playing answer..."):
                            text_to_speech(st.session_state.answer)
                        st.success("Playing audio!")
                    except ValueError as e:
                        st.error(f"Invalid input: {str(e)}")
                        logger.error(f"Validation error: {e}")
                    except RuntimeError as e:
                        st.error(f"Audio error: {str(e)}")
                        logger.error(f"Audio error: {e}")
                    except Exception as e:
                        st.error(f"Unexpected error: {str(e)}")
                        logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()

