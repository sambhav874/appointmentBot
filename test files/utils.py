import os
import csv
import json
from langchain_huggingface import HuggingFaceEmbeddings
import requests
from datetime import datetime
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from config import (GREETINGS, INSURANCE_KEYWORDS, BOOKING_KEYWORDS, CUSTOM_PROMPT_TEMPLATE, 
                    APPOINTMENTS_CSV_PATH, CHATBOT_DATA_PATH, db, SEARCH_DOCS)
from difflib import SequenceMatcher
from langchain.vectorstores import FAISS

# Load environment variables at the start
load_dotenv()

# Get the API key from environment variables
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
DB_FAISS_PATH = os.getenv('DB_FAISS_PATH')

# Token counting function
def count_tokens(text):
    return len(text.split())

# Load the custom prompt template
def set_custom_prompt():
    return PromptTemplate(template=CUSTOM_PROMPT_TEMPLATE, input_variables=['context', 'question'])

# Check if the query is a greeting
def is_greeting(query):
    return any(greet in query.lower().strip().split() for greet in GREETINGS)

# Check if the query is insurance-related using similarity
def is_insurance_related(query):
    query_words = query.lower().split()
    for keyword in INSURANCE_KEYWORDS:
        for word in query_words:
            if SequenceMatcher(None, keyword, word).ratio() > 0.8:
                return True
    return False

# Check if the query indicates booking intent
def is_booking_intent(query):
    return any(keyword in query.lower().split() for keyword in BOOKING_KEYWORDS)

# Book an appointment and save details
def appointment_booking():
    print("ADA: Let's book an appointment for you. I will need some details.")
    user_name = input("Please enter your name: ")
    contact_info = input("Please enter your contact information: ")
    preferred_date = input("Please enter your preferred date (YYYY-MM-DD): ")
    preferred_time = input("Please enter your preferred time (HH:MM): ")
    appointment_datetime = f"{preferred_date} {preferred_time}"
    
    # Save the appointment information to CSV
    with open(APPOINTMENTS_CSV_PATH, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([user_name, contact_info, appointment_datetime])
    
    print("ADA: Thank you! Your appointment has been booked.")
    return "Your appointment has been successfully scheduled."

# Validate response against the context
def validate_response(response, context):
    return response if any(word in response for word in context.split()) else "I don't know the answer."

# Save interaction to CSV file
def save_interaction(timestamp, query, ques_tok, answer, ans_tok, tokens_count):
    with open(CHATBOT_DATA_PATH, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, query, ques_tok, answer, ans_tok, tokens_count])

# Send a prompt to the Groq API and get response
def get_groq_response(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    data = {
        "model": "llama-3.2-3b-preview",
        "messages": [{
            "role": "user",
            "content": prompt
        }]
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error: Unable to get response. Status code: {response.status_code}"

# Get relevant context from FAISS database
def get_relevant_context(query):
    docs = db.similarity_search(query, k=SEARCH_DOCS)
    return " ".join([doc.page_content for doc in docs])

# Initialize embeddings and database if not already initialized
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)

# Generate and validate response
def generate_and_validate_response(query, prompt_template ):
    """
    Generate and validate response for a given query using Groq API with context from FAISS.
    """
    # Get relevant context from FAISS database
    context = get_relevant_context(query)
    
    # Format prompt with the query and context
    prompt = prompt_template.format(context=context, question=query)
    
    # Generate the response using Groq API
    answer = get_groq_response(prompt)
    
    # Validate response
    validated_answer = validate_response(answer, context)
    
    return validated_answer