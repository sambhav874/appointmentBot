from flask import Flask, request, jsonify
from flask_cors import CORS
from appointmentBot import InsuranceChatbot, validate_environment, create_data_directories

app = Flask(__name__)
CORS(app)

# Initialize chatbot
if validate_environment():
    create_data_directories()
    chatbot = InsuranceChatbot()
else:
    raise Exception("Environment validation failed")

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message')
        action = data.get('action', 'chat')  # Default action is chat
        
        if not message and action == 'chat':
            return jsonify({'error': 'No message provided'}), 400

        response_data = {
            'response': '',
            'state': chatbot.context.current_state,
            'userDetails': {
                'name': chatbot.context.user_name,
                'insuranceType': chatbot.context.insurance_type,
                'collectedInfo': chatbot.context.collected_info
            },
            'insuranceTypes': chatbot.config.INSURANCE_TYPES
        }

        # Handle different actions
        if action == 'chat':
            response = chatbot.process_message(message)
            response_data['response'] = response
            
        elif action == 'schedule':
            # Handle appointment scheduling
            appointment_details = {
                'name': data.get('name'),
                'email': data.get('email'),
                'mobile': data.get('mobile'),
                'insurance_type': data.get('insuranceType'),
                'preferred_date': data.get('preferredDate'),
                'preferred_time': data.get('preferredTime')
            }
            
            chatbot.context.set_user_name(appointment_details['name'])
            chatbot.context.set_insurance_type(appointment_details['insurance_type'])
            chatbot.save_user_data(appointment_details)
            chatbot.context.collected_info.update(appointment_details)
            
            response_data['response'] = f"Appointment scheduled for {appointment_details['preferred_date']} at {appointment_details['preferred_time']}"
            
        elif action == 'reset':
            chatbot.context = chatbot.ConversationContext()
            response_data['response'] = "Conversation reset successfully"
            
        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5005)