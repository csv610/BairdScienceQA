import json
import os
import random

from gtts import gTTS
import vlc
import streamlit as st
from llama_model import LlamaModel

# Load questions from a JSON file
@st.cache_data
def load_questions():
    with open('questions.json', 'r') as f:
        questions = json.load(f)
    return questions
    
@st.cache_data
def get_llm_model(model_name):
    return LlamaModel(model_name)

def initialize_remaining_questions(num_questions):
    """Initialize a set of remaining question indices."""
    return set(range(num_questions))

def generate_new_question(questions, remaining_questions):
    """Generate a new question from the remaining questions."""
    if remaining_questions:
        # Select a random index from the remaining questions
        random_index = random.choice(list(remaining_questions))
        selected_question = questions[random_index]  # Select the question using the random index
        
        # Remove the index from the remaining questions
        remaining_questions.remove(random_index)
        
        return selected_question  
    else:
        return None

def text_to_speech(text: str):
    """Convert text to speech and play it using VLC."""
    if not text:  # Check if the text is empty
        raise ValueError("Text cannot be empty.")
    
    tts = gTTS(text=text, lang='en')
    tts.save("answer.mp3")
    
    # Play the audio using VLC
    player = vlc.MediaPlayer("answer.mp3")
    player.play()

def reset_questions():
    """Reset the question and answer in session state."""
    st.session_state.question = None  # Reset question in session state
    st.session_state.answer = None  # Reset answer in session state

def main():
    st.sidebar.title("Science Questions")
    # Initialize a list to keep track of asked questions

    asked_questions = []
    if 'question' not in st.session_state:
        st.session_state.question = None  # Initialize question in session state
    if 'answer' not in st.session_state:
        st.session_state.answer = None  # Initialize answer in session state

    model_names = ['llama3.2', 'llama3.1', 'gemma2']
    model_name = st.sidebar.selectbox('Select a model', model_names)

    # Display questions for the selected subject
    questions = load_questions()
     
    subjects = questions.keys()  # Load subjects for the selectbox
    subject = st.sidebar.selectbox("Choose a subject", subjects, key='subject', on_change=reset_questions)

    questions = questions[subject]

    st.sidebar.write(f"Total questions: {len(questions)}")

    llm = get_llm_model(model_name)

    # Initialize the remaining questions set
    remaining_questions = initialize_remaining_questions(len(questions))

    # Add a button to generate a new random question
    if st.sidebar.button("New Question"):
        st.session_state.question = generate_new_question(questions, remaining_questions)  # Store in session state
        if st.session_state.question:
            st.session_state.answer = None  # Reset answer when a new question is generated
        else:
            st.write("No more questions available.")
            # Ask the user if they want to start over
            if st.button("Start Over"):
                remaining_questions = initialize_remaining_questions(len(questions))  # Reset remaining questions
                st.write("You can start asking questions again!")

    # Display the current question if it exists
    if st.session_state.question is not None:
        st.write(f"**Question:** {st.session_state.question}")

        # Create an "Ask LLM" button for the selected question
        if st.button("Ask LLM"):
            with st.spinner("Generating answer..."):  # Start spinner
                st.session_state.answer = llm.get_response(st.session_state.question)  # Store answer in session state
    
    # Create a "Speak Answer" button for the generated answer
    if st.session_state.answer is not None:
        st.write(f"**Answer:** {st.session_state.answer}")  # Ensure the answer is displayed
        if st.button("Speak Answer"):
            with st.spinner("Playing answer..."):  # Start spinner
                text_to_speech(st.session_state.answer)
    
if __name__ == "__main__":
    main()

