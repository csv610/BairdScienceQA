import streamlit as st
from llama_model import LlamaModel
import json
import random

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
st.sidebar.title("Select Subject")
subject = st.sidebar.selectbox("Choose a subject", list(load_questions().keys()))
questions = questions[subject]

model_names = ['llama3.2', 'llama3.1', 'gemma2']
model_name = st.sidebar.selectbox('Select a model', model_names)

llm = get_llm_model(model_name)

# Add a button to generate a new random question
if st.button("New Question"):
    question = random.choice(questions)
    st.write(f"**Question:** {question}")

    with st.spinner('Getting answer ...'):
        answer = llm.get_response(question)

    st.write(f"**Answer:** {answer}")


