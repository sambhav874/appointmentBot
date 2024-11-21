import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';



// Configuration
const config = {
  vus: 5,
  duration: '1m',
  iterations: 10,
};

export const options = {
  vus: config.vus,
  duration: config.duration,
  iterations: config.iterations,
};

const messages = [
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
];

function sendMessage(chatId, customMessage = null) {
  const message = customMessage || randomItem(messages);
  console.log(`Sending: ${message} - ${chatId}`);

  const url = 'localhost:5000/api/chat';
  const payload = JSON.stringify({ message });
  const params = {
    headers: {
      'Content-Type': 'application/json',
      
    },
  };

  const response = http.post(url, payload, params);
  

  check(response, {
    'status is 200': (r) => r.status === 200,
  });

  if (response.status !== 200) {
    console.error(`Error sending message: ${response.status} - ${response.body}`);
    
  }

  return { message, response };
}

export default function () {
  const chatId = `chat_${__VU}_${__ITER}`;
  let lastMessage;

  for (let i = 0; i < 5; i++) {
    
    const { message, response } = sendMessage(chatId);
    

    

    if (response.status === 200) {
      try {
        const jsonResponse = JSON.parse(response.body);
        const botResponse = jsonResponse.response;
        console.log(`Bot response: ${botResponse} - ${chatId}`);
        

        
      } catch (error) {
        console.error(`Error parsing response: ${error} - ${chatId}`);
        errorRate.add(1);
      }
    }
  }
}

// Note: The handleSummary function is not included as it's not directly applicable to the HTTP version.
// You would need to modify it to work with the HTTP metrics instead of WebSocket-specific data.

console.log('Load test completed. Check the k6 output for results.')