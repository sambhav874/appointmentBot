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
    
    # Conversation States
    CONVERSATION_STATES = {
        'GREETING': 'greeting',
        'COLLECTING_NAME': 'collecting_name',
        'UNDERSTANDING_NEED': 'understanding_need',
        'INSURANCE_DISCUSSION': 'insurance_discussion',
        'SCHEDULING_APPOINTMENT': 'scheduling_appointment',
        'FAREWELL': 'farewell'
    }
    
    # Relevance Keywords
    INSURANCE_KEYWORDS = [
        "insurance", "policy", "claim", "premium", "coverage", 
        "deductible", "benefit", "protection", "risk", "medical", 
        "health", "life", "auto", "home", "appointment", "schedule",
        "wing heights", "ghana"
    ]

    # Intent Configurations
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
            "details", "learn", "understand", "looking for insurance",
            "need insurance", "want insurance"
        ],
        'appointment_request': [
            "schedule", "book", "consultation", "meeting", 
            "appointment", "want to meet", "discuss"
        ],
        'problem_description': [
            "issue", "problem", "concern", "difficulty", 
            "challenge", "help", "need assistance"
        ]
    }

    # Response Templates
    RESPONSE_TEMPLATES = {
        'greeting': [
            "Hello! I'm ADA from Wing Heights Ghana. Let's schedule an insurance consultation for you. What type of insurance are you interested in?",
            "Hi! I'm ADA, your insurance assistant at Wing Heights Ghana. I can help you book a consultation. Which insurance type interests you?",
            "Welcome to Wing Heights Ghana! I'm ADA and I'll help schedule your insurance consultation. What insurance type would you like to discuss?"
        ],
        'name_greeting': [
            "Hello {name}! Let's schedule your insurance consultation. Which type of insurance interests you?",
            "Hi {name}! I'll help you book an insurance consultation. What type of insurance would you like to discuss?",
            "Great to meet you {name}! Let's set up your insurance consultation. Which insurance type are you considering?"
        ],
        'insurance_inquiry': [
            "Perfect, I can help you with {insurance_type}. Let's schedule a consultation to discuss the details. When would you like to meet?",
            "Great choice! For {insurance_type}, it's best to discuss options in person. Let me help you book a consultation.",
            "I understand you're interested in {insurance_type}. The best way forward is to schedule a consultation. When works for you?"
        ],
        'appointment_suggestion': [
            "Great, {name}! Let's schedule your {insurance_type} consultation.",
            "Perfect timing {name}! I'll help you book a consultation for {insurance_type}.",
            "Excellent choice {name}! Let's set up your {insurance_type} consultation."
        ],
        
    }

class ConversationContext:
    def __init__(self):
        self.user_name = None
        self.insurance_type = None
        self.current_state = Config.CONVERSATION_STATES['GREETING']
        self.collected_info = {}
        self.last_message = None
        self.appointment_suggested = False
        self.conversation_history = []
    
    def update_state(self, new_state):
        self.current_state = new_state
    
    def set_user_name(self, name):
        self.user_name = name
        self.collected_info['name'] = name
    
    def set_insurance_type(self, insurance_type):
        self.insurance_type = insurance_type
        self.collected_info['insurance_type'] = insurance_type
    
    def add_to_history(self, message, role='user'):
        self.conversation_history.append({
            'role': role,
            'content': message,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self.last_message = message

class IntentClassifier:
    @staticmethod
    def classify_intent(query, intents):
        """
        Classify the user's intent based on keyword matching.
        Returns the most likely intent and confidence score.
        """
        query_lower = query.lower()
        
        intent_matches = {}
        for intent, keywords in intents.items():
            matches = sum(1 for keyword in keywords if keyword in query_lower)
            if matches > 0:
                confidence = (matches / len(keywords)) * 100
                intent_matches[intent] = confidence
        
        if intent_matches:
            top_intent = max(intent_matches, key=intent_matches.get)
            return top_intent, intent_matches[top_intent]
        
        return 'general', 0


class UserInputCollector:
    @staticmethod
    def collect_user_details(insurance_types, context=None, prefilled_data=None):
        """Collect comprehensive user details with structured input."""
        print("\n--- Wing Heights Ghana Insurance Consultation Details ---")
        
        if context:
            print(f"{context}")
        
        # Initialize with prefilled data or empty dict
        details = prefilled_data or {}
        
        # Name collection (if not prefilled)
        if 'name' not in details:
            while True:
                name = input("Full Name: ").strip()
                if re.match(r'^[A-Za-z\s]{2,50}$', name):
                    details['name'] = name
                    break
                print("Invalid name. Use only alphabets (2-50 characters).")
        
        # Email collection
        while True:
            email = input("Email (optional, press Enter to skip): ").strip()
            if email == "" or re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                details['email'] = email or 'Not Provided'
                break
            print("Invalid email format. Please try again.")
        
        # Mobile number collection
        while True:
            mobile = input("Mobile Number: ").strip()
            if re.match(r'^[0-9]{10}$', mobile):
                details['mobile'] = mobile
                break
            print("Invalid mobile number. Use 10 digits.")
        
        # Insurance type (if not prefilled)
        if 'insurance_type' not in details:
            print("\nSelect Insurance Type:")
            for i, ins_type in enumerate(insurance_types, 1):
                print(f"{i}. {ins_type}")
            
            while True:
                try:
                    type_choice = input("Enter the number of your insurance type: ").strip()
                    details['insurance_type'] = insurance_types[int(type_choice) - 1]
                    break
                except (ValueError, IndexError):
                    print("Invalid selection. Please choose a number from the list.")
        
        # Date selection
        while True:
            date = input("Preferred Date (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(date, '%Y-%m-%d')
                details['preferred_date'] = date
                break
            except ValueError:
                print("Invalid date format. Use YYYY-MM-DD.")
        
        # Time selection
        while True:
            time = input("Preferred Time (HH:MM, 24-hour format): ").strip()
            try:
                datetime.strptime(time, '%H:%M')
                details['preferred_time'] = time
                break
            except ValueError:
                print("Invalid time format. Use HH:MM in 24-hour format.")
        
        details['appointment_needed'] = True
        return details

class InsuranceChatbot:
    def __init__(self):
        self.config = Config()
        self.client = Groq(api_key=self.config.GROQ_API_KEY)
        self.tokens_count = 0
        self.context = ConversationContext()
        
        self.messages = [
            {
                "role": "system", 
                "content": """
                1. You are ADA, Wing Heights Ghana's professional insurance consultation AI assistant.
                2. Properly reply to greetings and farewells.
                3. If the user introduces themselves, greet them by name and ask how you can assist them with their insurance needs.
                4. Be interactive and conversational.
                5. List the insurance types available and ask the user which one they are interested in.
                6. Only answer questions about insurance, appointment booking, or Wing Heights Ghana services. 
                7. For any other topics, don't give any answer and politely decline to answer."""
            }
        ]
    
    def extract_name(self, message):
        """Extract name from introduction messages."""
        name_patterns = [
            r"(?i)(?:i am|i'm|this is|name is|call me)\s+([A-Za-z]+)",
            r"(?i)^([A-Za-z]+)\s+here",
            r"(?i)^hi|hello|hey\s+(?:this is\s+)?([A-Za-z]+)"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1)
        return None

    def handle_greeting(self, message):
        """Handle greeting messages."""
        name = self.extract_name(message)
        if name:
            name = name.capitalize()
            self.context.set_user_name(name)
            return self.format_response('name_greeting', name=name)
        return self.format_response('greeting')

    def extract_insurance_type(self, message):
        """Extract insurance type from user message."""
        for insurance_type in self.config.INSURANCE_TYPES:
            if insurance_type.lower() in message.lower():
                return insurance_type
        return None

    def format_response(self, template_key, **kwargs):
        """Format response template with provided context."""
        templates = self.config.RESPONSE_TEMPLATES.get(template_key, [])
        if not templates:
            return None
        
        template = random.choice(templates)
        return template.format(**kwargs)

    def generate_contextual_response(self):
        """Generate response based on current conversation state and context."""
        if self.context.current_state == Config.CONVERSATION_STATES['GREETING']:
            return self.format_response('greeting')
        
        elif self.context.current_state == Config.CONVERSATION_STATES['UNDERSTANDING_NEED']:
            if self.context.insurance_type:
                return self.format_response('insurance_inquiry', 
                                         insurance_type=self.context.insurance_type)
            return "What type of insurance from Wing Heights Ghana are you interested in?"
        
        elif self.context.current_state == Config.CONVERSATION_STATES['INSURANCE_DISCUSSION']:
            return self.format_response('appointment_suggestion',
                                     insurance_type=self.context.insurance_type)
        
        return self.get_ai_response(self.context.last_message)



    def process_message(self, message):
        """Process incoming message and update context."""
        self.context.add_to_history(message)
        
        # Check for greeting intent first
        intent_classifier = IntentClassifier()
        intent, confidence = intent_classifier.classify_intent(message.lower(), self.config.INTENTS)
        
        # Handle greetings
        if intent == 'greeting':
            return self.handle_greeting(message)
        
        # Handle farewells
        if intent == 'farewell':
            self.context.update_state(Config.CONVERSATION_STATES['FAREWELL'])
            return self.handle_farewell()
        
        # Extract name if not already known
        if not self.context.user_name:
            name = self.extract_name(message)
            if name:
                self.context.set_user_name(name)
                self.context.update_state(Config.CONVERSATION_STATES['UNDERSTANDING_NEED'])
                return self.format_response('name_greeting', name=name)
        
        # Extract insurance type if in appropriate state
        if self.context.current_state == Config.CONVERSATION_STATES['UNDERSTANDING_NEED']:
            insurance_type = self.extract_insurance_type(message)
            if insurance_type:
                self.context.set_insurance_type(insurance_type)
                self.context.update_state(Config.CONVERSATION_STATES['INSURANCE_DISCUSSION'])
                return self.format_response('insurance_inquiry', 
                                         insurance_type=self.context.insurance_type)
        
        # Handle appointment scheduling
        if "yes" in message.lower() and self.context.current_state == Config.CONVERSATION_STATES['INSURANCE_DISCUSSION']:
            self.context.update_state(Config.CONVERSATION_STATES['SCHEDULING_APPOINTMENT'])
            return self.schedule_appointment()
        
        # If no specific condition is met, get AI response
        return self.get_ai_response(message)

   
    def get_ai_response(self, query):
        """Generate AI response with context awareness."""
        try:
            # Add context to the query
            context_query = query
            if self.context.user_name:
                context_query = f"[User: {self.context.user_name}] {query}"
            if self.context.insurance_type:
                context_query = f"[Insurance: {self.context.insurance_type}] {context_query}"
            
            self.messages.append({
                "role": "user",
                "content": context_query
            })
            
            chat_completion = self.client.chat.completions.create(
                messages=self.messages,
                model="llama-3.2-3b-preview",
                temperature=0.7,
                max_tokens=self.config.MAX_RESPONSE_TOKENS,
            )
            
            response = chat_completion.choices[0].message.content
            
            self.messages.append({
                "role": "assistant",
                "content": response
            })
            
            return response
        
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"

    def schedule_appointment(self):
        """Enhanced appointment scheduling with context awareness."""
        print(f"\nADA: Great! Let's schedule your {self.context.insurance_type} consultation with Wing Heights Ghana.")
        
        # Pre-fill known information
        prefilled_data = {
            'name': self.context.user_name,
            'insurance_type': self.context.insurance_type
        }
        
        appointment_details = UserInputCollector.collect_user_details(
            self.config.INSURANCE_TYPES,
            context=f"Scheduling {self.context.insurance_type} consultation with Wing Heights Ghana",
            prefilled_data=prefilled_data
        )
        
        self.save_user_data(appointment_details)
        self.context.collected_info.update(appointment_details)
        
        return (f"Perfect! I've scheduled your {self.context.insurance_type} consultation with Wing Heights Ghana for "
                f"{appointment_details['preferred_date']} at {appointment_details['preferred_time']}. "
                f"Is there anything else you'd like to know about our insurance services?")

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
        interaction_data = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'name': self.context.user_name or 'Unknown',
            'insurance_type': self.context.insurance_type or 'Not Specified',
            'query': query,
            'response': response,
            'conversation_state': self.context.current_state,
            'query_tokens': len(query.split()),
            'response_tokens': len(response.split())
        }
        
        file_exists = os.path.exists(self.config.CHATBOT_DATA_PATH)
        
        with open(self.config.CHATBOT_DATA_PATH, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=interaction_data.keys())
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(interaction_data)

    def count_tokens(self, text):
        """Simple token counting."""
        return len(text.split())

    def handle_farewell(self):
        """Handle farewell state with context-aware goodbye."""
        farewell_messages = [
            "Goodbye! Thank you for choosing Wing Heights Ghana for your insurance needs.",
            "Have a great day! Feel free to return if you have more questions about our insurance services.",
            "Take care! Don't hesitate to reach out if you need anything else regarding our insurance offerings."
        ]
        return random.choice(farewell_messages)

    def run(self):
        """Enhanced chatbot interaction flow with context management."""
        print("\nADA: Hello! I'm ADA, your friendly AI assistant.")
        print("     I'm here to help you with any questions you may have.")
        print("     Feel free to introduce yourself and let me know what brings you here today!\n")
        
        while self.tokens_count <= self.config.MAX_SESSION_TOKENS:
            try:
                query = input("YOU: ").strip()
                
                # Handle exit conditions
                if query.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                    self.context.update_state(Config.CONVERSATION_STATES['FAREWELL'])
                    farewell = self.handle_farewell()
                    print(f"ADA: {farewell}")
                    break
                
                # Process message and get response
                response = self.process_message(query)
                print(f"ADA: {response}")
                
                # Save interaction
                self.save_interaction(query, response)
                
                # Update token count
                self.tokens_count += (self.count_tokens(query) + self.count_tokens(response))
                
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
                break

def validate_environment():
    """Validate environment setup and requirements."""
    required_files = ['.env']
    required_vars = ['GROQ_API_KEY']
    
    # Check required files
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"Missing required files: {', '.join(missing_files)}")
        return False
    
    # Check required environment variables
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    return True

def create_data_directories():
    """Create necessary directories for data storage."""
    directories = ['data', 'logs']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def main():
    """Main function to run the chatbot."""
    print("\nInitializing Wing Heights Ghana Insurance Consultation Chatbot...")
    
    # Validate environment
    if not validate_environment():
        print("Environment validation failed. Please check the requirements and try again.")
        return
    
    # Create necessary directories
    create_data_directories()
    
    try:
        # Initialize and run chatbot
        chatbot = InsuranceChatbot()
        chatbot.run()
    except KeyboardInterrupt:
        print("\nChatbot terminated by user.")
    except Exception as e:
        print(f"\nAn error occurred while running the chatbot: {str(e)}")
    finally:
        print("\nChatbot session ended.")

if __name__ == "__main__":
    main()