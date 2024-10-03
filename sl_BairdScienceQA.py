import streamlit as st
from llama_model import LlamaModel
import json
import random

# Load questions from a JSON file
@st.cache_data
def load_questions(subject):
    with open('questions.json', 'r') as f:
        Questions = json.load(f)
    return [q for q in Questions if q['subject'] == subject]

@st.cache_data
def get_llm_model(model_name):
    return LlamaModel(model_name)

# Sidebar menu for selecting the subject
st.sidebar.title("Select Subject")
subject = st.sidebar.selectbox("Choose a subject", list(load_questions().keys()))

# Display questions for the selected subject
questions = load_questions(subject)

model_names = ['llama3.2', 'llama3.1', 'gemma2']
model_name = st.selectbox('Select a model', model_names)

llm = get_llm_model(model_name)

# Add a button to generate a new random question
if st.button("New Question"):
    question = random.choice(questions)
    st.write(f"Question: {question}")

# Create an "Ask LLM" button for the selected question
if st.button("Ask LLM"):
    answer = llm.get_response(question)
    st.write(f"LLM's answer to: {answer}")


