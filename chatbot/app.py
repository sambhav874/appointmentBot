from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot import InsuranceChatbot

app = Flask(__name__)
CORS(app)

chatbot = InsuranceChatbot()

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message')
    
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400
    
    response = chatbot.handle_intent(user_input)
    
    # Check if the response suggests scheduling an appointment
    if chatbot.suggests_need_for_appointment(user_input) and not chatbot.appointment_scheduled:
        response += " Would you like to schedule an appointment? (yes/no)"
    
    # Handle appointment scheduling
    if user_input.lower() == 'yes' and not chatbot.appointment_scheduled:
        appointment_details = chatbot.schedule_appointment()
        response = f"Great! {appointment_details}"
    
    chatbot.save_interaction(user_input, response)
    
    return jsonify({
        'response': response,
        'intent': chatbot.current_intent,
        'appointment_scheduled': chatbot.appointment_scheduled
    })

@app.route('/sentiment_analysis', methods=['GET'])
def get_sentiment_analysis():
    sentiment_stats = chatbot.sentiment_analyzer.get_sentiment_stats(chatbot.conversation_sentiments)
    return jsonify(sentiment_stats)

if __name__ == '__main__':
    app.run(debug=True , port=5005)