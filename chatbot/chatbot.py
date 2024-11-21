import csv
import json
from datetime import datetime
from groq import Groq
import random
import os

from config import Config
from intentClassifier import IntentClassifier
from userInputs import UserInputCollector
from sentimentAnalyser import SentimentAnalyzer

class InsuranceChatbot:
    def __init__(self):
        self.config = Config()
        self.client = Groq(api_key=self.config.GROQ_API_KEY)
        self.tokens_count = 0
        self.user_details = None
        self.appointment_scheduled = False
        self.current_intent = None
        self.sentiment_analyzer = SentimentAnalyzer()
        self.conversation_sentiments = []
        
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
        
        sentiment_label, sentiment_score = self.sentiment_analyzer.analyze_sentiment(query)
        self.conversation_sentiments.append(sentiment_label)
        
        interaction_data = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'name': self.user_details.get('name', 'Unknown'),
            'insurance_type': self.user_details.get('insurance_type', 'Not Specified'),
            'query': query,
            'response': response,
            'current_intent': self.current_intent,
            'query_tokens': self.count_tokens(query),
            'response_tokens': self.count_tokens(response),
            'sentiment_label': sentiment_label,
            'sentiment_score': sentiment_score
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
        
        # Print sentiment analysis at the end of the conversation
        sentiment_stats = self.sentiment_analyzer.get_sentiment_stats(self.conversation_sentiments)
        print("\nConversation Sentiment Analysis:")
        print(f"Positive: {sentiment_stats['percentages']['positive']:.2f}%")
        print(f"Neutral: {sentiment_stats['percentages']['neutral']:.2f}%")
        print(f"Negative: {sentiment_stats['percentages']['negative']:.2f}%")

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