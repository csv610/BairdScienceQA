import streamlit as st
from llama_model import LlamaModel
import json
import random
import time

@st.cache_data
def load_questions():
    try:
        with open('questions.json', 'r') as f:
            questions = json.load(f)
            return questions
    except json.JSONDecodeError:
        st.error("Error: The JSON file is invalid or empty.")
        return None
    except FileNotFoundError:
        st.error("Error: The questions.json file was not found.")
        return None


@st.cache_data
def get_llm_model(model_name):
    return LlamaModel(model_name)

# Display questions for the selected subject
questions = load_questions()

# Sidebar menu for selecting the subject
st.sidebar.title("Science Questions")
subject = st.sidebar.selectbox("Choose a subject", list(load_questions().keys()))
questions = questions[subject]

model_names = ['llama3.2', 'llama3.1', 'gemma2']
model_name = st.sidebar.selectbox('Select a model', model_names)

llm = get_llm_model(model_name)

# Add a button to generate a new random question
if st.sidebar.button("New Question"):
    question = random.choice(questions)
    st.write(f"**Question:** {question}")

    with st.spinner('Getting answer...'):
         start_time = time.time()  # Record the start time
         answer = llm.get_response(question)  # Get the response from the model
         elapsed_time = time.time() - start_time  # Calculate the elapsed time

    word_count = len(answer.split())
    st.write(f"**Answer:** {answer}")
    st.write(f"**Word Count:** {word_count} words")
    st.write(f"**Elapsed Time:** {elapsed_time:.2f} seconds")


