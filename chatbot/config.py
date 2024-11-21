import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Settings
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    
    # Paths
    CHATBOT_DATA_PATH = "chatbot_data.csv"
    APPOINTMENTS_CSV_PATH = "appointments.csv"
    USER_DATA_PATH = "user_data.csv"
    
    # Insurance Types
    INSURANCE_TYPES = [
        "Health Insurance", 
        "Life Insurance", 
        "Auto Insurance", 
        "Home Insurance", 
        "Travel Insurance", 
        "Business Insurance"
    ]
    
    # Token Limits
    MAX_SESSION_TOKENS = 2000
    MAX_RESPONSE_TOKENS = 300
    
    # Relevance Keywords
    INSURANCE_KEYWORDS = [
        "insurance", "policy", "claim", "premium", "coverage", 
        "deductible", "benefit", "protection", "risk", "medical", 
        "health", "life", "auto", "home", "appointment", "schedule"
    ]

    # Intent-related configurations
    INTENTS = {
        'greeting': [
            "hello", "hi", "hey", "greetings", "good morning", 
            "good afternoon", "good evening", "howdy"
        ],
        'farewell': [
            "bye", "goodbye", "see you", "talk to you later", 
            "exit", "quit"
        ],
        'insurance_inquiry': [
            "what", "how", "explain", "tell me about", "information", 
            "details", "learn", "understand"
        ],
        'appointment_request': [
            "schedule", "book", "consultation", "meeting", 
            "appointment", "want to meet", "discuss"
        ],
        'problem_description': [
            "issue", "problem", "concern", "difficulty", 
            "challenge", "help", "need assistance"
        ],
        'claim_related': [
            "claim", "compensation", "insurance claim", 
            "filing claim", "submit claim"
        ]
    }

    # Greeting responses with variations
    GREETING_RESPONSES = [
        "Hello! I'm ADA, your insurance consultation assistant. How can I help you today?",
        "Hi there! Welcome to our insurance support service. What can I assist you with?",
        "Greetings! I'm here to provide expert guidance on insurance matters. What would you like to know?",
        "Good day! I'm ADA, ready to help you navigate your insurance needs. What questions do you have?",
        "Welcome! I'm your dedicated insurance consultation assistant. How can I support you today?"
    ]

    # Additional contextual responses
    INTENT_CONTEXT_RESPONSES = {
        'insurance_inquiry': [
            "Great question! I'm happy to provide detailed information about insurance.",
            "Let me help you understand the specifics of insurance coverage.",
            "Insurance can be complex, but I'll break it down for you clearly."
        ],
        'claim_related': [
            "Claims can be intricate. I'll guide you through the process step by step.",
            "Filing a claim requires careful attention. Let's go through the details together.",
            "I'm here to support you through the claim process."
        ],
        'appointment_request': [
            "A personalized consultation is an excellent way to address your specific insurance needs.",
            "Scheduling an appointment will help us dive deep into your insurance requirements.",
            "Let's find the perfect time for a comprehensive insurance consultation."
        ]
    }