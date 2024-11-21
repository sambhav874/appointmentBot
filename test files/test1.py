import time
import random
from locust import HttpUser, task, between
from locust.contrib.fasthttp import FastHttpUser
import websocket

class ChatbotUser(FastHttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.ws = websocket.create_connection("wss://srv618269.hstgr.cloud/socket.io/?EIO=4&transport=websocket")
        self.ws.recv()  # Receive the initial message
        self.ws.send("40")  # Send the connection message

    @task
    def send_message(self):
        messages = [
            'What insurance policies do you offer?',
            'How much does life insurance cost?',
            'Can I get a quote for car insurance?',
            'What documents do I need for health insurance?',
            'How do I file a claim?',
            'What are the learning outcomes of introduction to insurances?',
            'Subrogation and contribution arise from?',
            'What are the principles of insurance?',
            'What is risk in insurances?',
            'What are the additional coverages in Shopkeepers Package Policy',
            'What are the types of insurance policies offered by the company?',
            'What are the Risks faced by business enterprises?',
            'What kind of covers are usually available under travel insurance?',
            'Give two examples explain the concept of insurance.',
            'List some Risks and perils.'
        ]
        message = random.choice(messages)
        self.ws.send(f'42["message",{{"message":"{message}"}}]')
        response = self.ws.recv()
        time.sleep(5)  # Wait for 5 seconds before sending the next message

    def on_stop(self):
        self.ws.close()

class WebsiteUser(HttpUser):
    tasks = [ChatbotUser]
    wait_time = between(5, 15)