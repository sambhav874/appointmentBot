from datetime import datetime
from config import MAX_SESSION_TOKENS
from utils import (count_tokens, set_custom_prompt, is_greeting, is_booking_intent, appointment_booking, 
                   is_insurance_related, generate_and_validate_response, save_interaction)

# Main chatbot function to interact with user
def qa_bot():
    prompt_template = set_custom_prompt()
    tokens_count = 0

    while tokens_count <= MAX_SESSION_TOKENS:
        query = input("YOU: ")
        ques_tok = count_tokens(query)
        tokens_count += ques_tok
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Handle greetings
        if is_greeting(query):
            greet_response = "ADA: Hello! How can I assist you with insurance-related questions today?"
            print(f"{greet_response} [Timestamp: {timestamp}]")
            tokens_count += count_tokens(greet_response)
            continue

        # Handle appointment booking
        if is_booking_intent(query):
            booking_response = appointment_booking()
            print(f"ADA: {booking_response} [Timestamp: {timestamp}]")
            tokens_count += count_tokens(booking_response)
            continue

        # Generate and validate response
        validated_answer = generate_and_validate_response(query, prompt_template)

        # Token counts and logging
        ans_tok = count_tokens(validated_answer)
        tokens_count += ans_tok
        print(f"ADA: {validated_answer} [Timestamp: {timestamp}]")
        print(f"Tokens used: Question - {ques_tok}, Answer - {ans_tok}, Total - {tokens_count}")
        save_interaction(timestamp, query, ques_tok, validated_answer, ans_tok, tokens_count)

    # End session
    print("ADA: Thank you for chatting! The conversation has ended.")
    print("ADA: You have reached the token limit! Please contact support.")

if __name__ == "__main__":
    qa_bot()