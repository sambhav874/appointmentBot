import os
import csv
import json
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
import re
import random

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

class IntentClassifier:
    @staticmethod
    def classify_intent(query, intents):
        """
        Classify the user's intent based on keyword matching.
        Returns the most likely intent and confidence score.
        """
        query_lower = query.lower()
        
        # Check for multi-word intents first
        intent_matches = {}
        for intent, keywords in intents.items():
            # Count matches
            matches = sum(1 for keyword in keywords if keyword in query_lower)
            
            # Calculate confidence based on number of matches and query length
            if matches > 0:
                # Adjust confidence calculation
                confidence = (matches / len(keywords)) * 100
                intent_matches[intent] = confidence
        
        # Return the intent with highest confidence
        if intent_matches:
            top_intent = max(intent_matches, key=intent_matches.get)
            return top_intent, intent_matches[top_intent]
        
        return 'general', 0

class UserInputCollector:
    @staticmethod
    def collect_user_details(insurance_types, context=None):
        """Collect comprehensive user details with structured input."""
        print("\n--- Insurance Consultation Details ---")
        
        # Provide context if available
        if context:
            print(f"{context}")
        
        # Name collection with validation
        while True:
            name = input("Full Name: ").strip()
            if re.match(r'^[A-Za-z\s]{2,50}$', name):
                break
            print("Invalid name. Use only alphabets (2-50 characters).")
        
        # Email collection with basic validation (optional)
        while True:
            email = input("Email (optional, press Enter to skip): ").strip()
            if email == "" or re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                break
            print("Invalid email format. Please try again.")
        
        # Mobile number collection
        while True:
            mobile = input("Mobile Number: ").strip()
            if re.match(r'^[0-9]{10}$', mobile):
                break
            print("Invalid mobile number. Use 10 digits.")
        
        # Insurance type selection
        print("\nSelect Insurance Type:")
        for i, ins_type in enumerate(insurance_types, 1):
            print(f"{i}. {ins_type}")
        
        while True:
            try:
                type_choice = input("Enter the number of your insurance type: ").strip()
                insurance_type = insurance_types[int(type_choice) - 1]
                break
            except (ValueError, IndexError):
                print("Invalid selection. Please choose a number from the list.")
        
        # Date selection
        while True:
            date = input("Preferred Date (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(date, '%Y-%m-%d')
                break
            except ValueError:
                print("Invalid date format. Use YYYY-MM-DD.")
        
        # Time selection
        while True:
            time = input("Preferred Time (HH:MM, 24-hour format): ").strip()
            try:
                datetime.strptime(time, '%H:%M')
                break
            except ValueError:
                print("Invalid time format. Use HH:MM in 24-hour format.")
        
        return {
            'name': name,
            'email': email or 'Not Provided',
            'mobile': mobile,
            'insurance_type': insurance_type,
            'preferred_date': date,
            'preferred_time': time,
            'appointment_needed': True
        }

class InsuranceChatbot:
    def __init__(self):
        self.config = Config()
        self.client = Groq(api_key=self.config.GROQ_API_KEY)
        self.tokens_count = 0
        self.user_details = None
        self.appointment_scheduled = False
        self.current_intent = None
        
        # Initialize conversation with enhanced system context
        self.messages = [
            {
                "role": "system", 
                "content": """You are ADA, a professional insurance consultation AI assistant. 
                Your primary goals are to:
                1. Understand the user's specific insurance-related intent
                2. Provide accurate, empathetic, and concise information
                3. Guide users towards scheduling a consultation if needed
                4. Maintain a professional yet friendly tone
                5. Adapt your responses to the user's specific insurance needs
                6. Offer clear, actionable advice about insurance matters"""
            }
        ]
    
    def handle_intent(self, query):
        """
        Dynamically handle different user intents with specialized responses.
        """
        # Classify intent
        intent, confidence = IntentClassifier.classify_intent(
            query, 
            self.config.INTENTS
        )
        
        # Store current intent
        self.current_intent = intent
        
        # Intent-specific handling
        if intent == 'greeting':
            return random.choice(self.config.GREETING_RESPONSES)
        
        elif intent == 'farewell':
            return "Thank you for your consultation. Have a great day!"
        
        elif intent in ['appointment_request', 'problem_description']:
            if not self.appointment_scheduled:
                context_response = random.choice(
                    self.config.INTENT_CONTEXT_RESPONSES.get(intent, 
                    ["I'm here to help you with your insurance needs."])
                )
                return f"{context_response} Would you like to schedule a personalized consultation?"
        
        elif intent == 'claim_related':
            return "For claim-related inquiries, we'll need to gather some specific information. Would you like to discuss your claim in more detail?"
        
        # If no specific intent handling, use AI response generation
        return self.get_ai_response(query)
    
    def is_query_relevant(self, query):
        """
        Enhanced relevance check with intent-based filtering.
        """
        intent, confidence = IntentClassifier.classify_intent(
            query, 
            self.config.INTENTS
        )
        
        # Consider intents and keywords
        return (
            confidence > 30 or  # Sufficient intent confidence
            any(keyword in query.lower() for keyword in self.config.INSURANCE_KEYWORDS)
        )
    
    def suggests_need_for_appointment(self, query):
        """
        Enhanced appointment suggestion detection using intent classification.
        """
        intent, confidence = IntentClassifier.classify_intent(
            query, 
            self.config.INTENTS
        )
        
        return (
            intent in ['appointment_request', 'problem_description'] or
            confidence > 50  # High confidence in consultation-related intent
        )
    
    def count_tokens(self, text):
        """Simple token counting."""
        return len(text.split())
    
    def save_user_data(self, user_details):
        """Save user details to CSV."""
        file_exists = os.path.exists(self.config.USER_DATA_PATH)
        
        with open(self.config.USER_DATA_PATH, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=user_details.keys())
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(user_details)
    
    def save_interaction(self, query, response):
        """Save interaction details to CSV."""
        if not self.user_details:
            return
        
        interaction_data = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'name': self.user_details.get('name', 'Unknown'),
            'insurance_type': self.user_details.get('insurance_type', 'Not Specified'),
            'query': query,
            'response': response,
            'current_intent': self.current_intent,
            'query_tokens': self.count_tokens(query),
            'response_tokens': self.count_tokens(response)
        }
        
        file_exists = os.path.exists(self.config.CHATBOT_DATA_PATH)
        
        with open(self.config.CHATBOT_DATA_PATH, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=interaction_data.keys())
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(interaction_data)
    
    def get_ai_response(self, query):
        """Generate AI response with token and relevance management."""
        try:
            # Check query relevance
            if not self.is_query_relevant(query):
                return "I apologize, but I can only assist with insurance-related queries. Could you rephrase your question?"
            
            # Add user message to conversation
            self.messages.append({
                "role": "user", 
                "content": query
            })
            
            # Generate response
            chat_completion = self.client.chat.completions.create(
                messages=self.messages,
                model="llama-3.2-3b-preview",
                temperature=0.7,
                max_tokens=self.config.MAX_RESPONSE_TOKENS,
            )
            
            # Extract and process response
            response = chat_completion.choices[0].message.content
            
            # Add AI response to conversation
            self.messages.append({
                "role": "assistant", 
                "content": response
            })
            
            return response
        
        except Exception as e:
            return f"An error occurred: {str(e)}"
    
    def schedule_appointment(self):
        """Schedule an appointment with user input."""
        print("ADA: Great! Let's schedule your insurance consultation.")
        context = "We'll now collect some details for your personalized consultation."
        
        appointment_details = UserInputCollector.collect_user_details(
            self.config.INSURANCE_TYPES,
            context
        )
        
        # Save appointment details
        self.save_user_data(appointment_details)
        self.user_details = appointment_details
        self.appointment_scheduled = True
        
        print(f"\nADA: Perfect! Your {appointment_details['insurance_type']} consultation is scheduled for {appointment_details['preferred_date']} at {appointment_details['preferred_time']}.")
        return "Appointment scheduled successfully."
    
    def run(self):
        """Enhanced chatbot interaction flow with intent-based routing."""
        print("\nADA: Hello! I'm ADA, your friendly insurance consultation assistant.")
        print("     I'm here to help you understand and navigate your insurance needs.")
        print("     Feel free to ask me anything about insurance or schedule a consultation.\n")
        
        while self.tokens_count <= self.config.MAX_SESSION_TOKENS:
            try:
                # Get user query
                query = input("YOU: ").strip()
                
                # Exit condition
                if query.lower() in ['exit', 'quit', 'bye']:
                    print("ADA: Thank you for your consultation. Have a great day!")
                    break
                
                # Handle intent and get response
                response = self.handle_intent(query)
                
                # Appointment suggestion logic
                if self.suggests_need_for_appointment(query) and not self.appointment_scheduled:
                    book_appointment = input("ADA: It sounds like you might benefit from a personalized consultation. Would you like to schedule an appointment? (yes/no): ").lower().strip()
                    
                    if book_appointment == 'yes':
                        self.schedule_appointment()
                        continue
                
                # Save interaction
                self.save_interaction(query, response)
                
                # Print response
                print(f"ADA: {response}")
                
                # Update token count
                self.tokens_count += (self.count_tokens(query) + self.count_tokens(response))
                
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break

def main():
    # Ensure .env file exists and has GROQ_API_KEY
    if not os.path.exists('.env'):
        print("Please create a .env file with your GROQ_API_KEY")
        return
    
    # Validate API Key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("GROQ_API_KEY is missing in the .env file")
        return
    
    # Run chatbot
    chatbot = InsuranceChatbot()
    chatbot.run()

if __name__ == "__main__":
    main()