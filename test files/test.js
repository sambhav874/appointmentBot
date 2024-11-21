import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import ws from 'k6/ws';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// Custom metrics
const errorRate = new Rate('errors');
const responseTime = new Trend('response_time');
const botResponseLength = new Trend('bot_response_length');
const connectionTime = new Trend('connection_time');
const messagesSent = new Counter('messages_sent');
const reconnectionAttempts = new Counter('reconnection_attempts');

// Configuration
const config = {
  vus: 5,
  
  duration: '15m',
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
  'What are the types of insurance policies offered by the company?',
  'What are the Risks faced by business enterprises?',
  'What kind of covers are usually available under travel insurance?',
  'Give two examples explain the concept of insurance.',
  'List some Risks and perils.'
];

function sendMessage(socket, chatId, customMessage = null) {
  const message = customMessage || randomItem(messages);
  console.log(`Sending: ${message} - ${chatId}`);

  const messageTimestamp = Date.now();
  socket.send(`42["message",{"message":"${message}"}]`);
  messagesSent.add(1);

  return { message, timestamp: messageTimestamp };
}

function setupWebSocket(chatId) {
  const url = 'wss://srv618269.hstgr.cloud/socket.io/?EIO=4&transport=websocket';
  const params = { 
    headers: { 'Origin': 'https://srv618269.hstgr.cloud' },
    transports: ['websocket', 'polling'],
    pingTimeout: 300000,  
    pingInterval: 60000, 
  };

  return new Promise((resolve, reject) => {
    const connectionStartTime = Date.now();
    const res = ws.connect(url, params, function (socket) {
      console.log(`Connected to WebSocket - ${chatId}`);
      let lastMessage;
      let chatMetrics = {
        id: chatId,
        connectionStartTime: connectionStartTime,
        messages: []
      };

      socket.on('open', () => {
        console.log(`WebSocket connection opened - ${chatId}`);
        chatMetrics.connectionTime = Date.now() - connectionStartTime;
        connectionTime.add(chatMetrics.connectionTime);
      });

      socket.on('message', (data) => {
        console.log(`Received: ${data} - ${chatId}`);
        chatMetrics.messages.push({ type: 'received', data, timestamp: Date.now() });

        if (data.startsWith('0')) {
          console.log(`Sending connection message - ${chatId}`);
          socket.send('40');
        } else if (data === '40') {
          console.log(`Connection confirmed, sending first message - ${chatId}`);
          lastMessage = sendMessage(socket, chatId);
          chatMetrics.messages.push({ type: 'sent', data: lastMessage.message, timestamp: lastMessage.timestamp });
        } else if (data.startsWith('42')) {
          try {
            const parsedData = JSON.parse(data.slice(2));
            if (Array.isArray(parsedData) && parsedData.length > 1 && typeof parsedData[1] === 'object') {
              const response = parsedData[1].response;
              if (response) {
                console.log(`Bot response: ${response} - ${chatId}`);
                const currentTime = Date.now();

                botResponseLength.add(response.length);
                
                if (lastMessage && currentTime > lastMessage.timestamp) {
                  responseTime.add(currentTime - lastMessage.timestamp);
                }

                if (response.includes("Please answer with 'Yes' or 'No'")) {
                  console.log(`Detected 'Yes' or 'No' question, sending 'No' - ${chatId}`);
                  sleep(1);
                  lastMessage = sendMessage(socket, chatId, "No");
                } else {
                  console.log(`Waiting before sending next message - ${chatId}`);
                  sleep(5);
                  lastMessage = sendMessage(socket, chatId);
                }
                chatMetrics.messages.push({ type: 'sent', data: lastMessage.message, timestamp: lastMessage.timestamp });
              }
            }
          } catch (error) {
            console.error(`Error parsing response: ${error} - ${chatId}`);
            errorRate.add(1);
            chatMetrics.messages.push({ type: 'error', message: error.toString(), timestamp: Date.now() });
          }
        }
      });

      socket.on('close', () => {
        console.log(`WebSocket connection closed - ${chatId}`);
        chatMetrics.endTime = Date.now();
        reject(new Error('WebSocket closed unexpectedly'));
      });

      socket.on('error', (e) => {
        console.error(`WebSocket error: ${e} - ${chatId}`);
        errorRate.add(1);
        chatMetrics.messages.push({ type: 'error', message: e.toString(), timestamp: Date.now() });
        reject(e);
      });

      resolve({ socket, chatMetrics });
    });

    check(res, { 'status is 101': (r) => r && r.status === 101 });
  });
}

let allChatMetrics = [];

export default function () {
  const chatId = `chat_${__VU}_${__ITER}`;
  let retries = 3;
  let socket, chatMetrics;

  while (retries > 0) {
    try {
      ({ socket, chatMetrics } = setupWebSocket(chatId));
      break;
    } catch (error) {
      console.error(`Connection failed for ${chatId}. Retrying... (${retries} attempts left)`);
      retries--;
      reconnectionAttempts.add(1);
      sleep(5);
    }
  }

  if (!socket) {
    console.error(`Failed to establish connection for ${chatId} after multiple attempts`);
    errorRate.add(1);
  } else {
    allChatMetrics.push(chatMetrics);
  }
}

export function handleSummary(data) {
  const summary = {
    metrics: data.metrics,
    chatMetrics: allChatMetrics,
  };

  let detailedSummary = textSummary(data, { indent: ' ', enableColors: true });
  detailedSummary += '\n\nConnection Analysis:\n';
  allChatMetrics.forEach((chat, index) => {
    detailedSummary += connectionSummary(chat, index);
  });

  return {
    'summary.json': JSON.stringify(summary, null, 2),
    stdout: detailedSummary,
  };
}

function textSummary(data, options) {
  const { metrics, root_group } = data;
  const { iterations, vus, vus_max } = options;

  return `
Summary:
  Scenarios: ${root_group.name}
  Iterations: ${iterations || 'N/A'}
  VUs: ${vus || 'N/A'} (max: ${vus_max || 'N/A'})

Metrics:
  Errors: ${metrics.errors ? metrics.errors.rate.toFixed(2) : 'N/A'}%
  Response time (avg): ${metrics.response_time ? metrics.response_time.avg.toFixed(2) : 'N/A'}ms
  Bot response length (avg): ${metrics.bot_response_length ? metrics.bot_response_length.avg.toFixed(2) : 'N/A'} characters
  Connection time (avg): ${metrics.connection_time ? metrics.connection_time.avg.toFixed(2) : 'N/A'}ms
  Messages sent: ${metrics.messages_sent ? metrics.messages_sent.count : 'N/A'}
  Reconnection attempts: ${metrics.reconnection_attempts ? metrics.reconnection_attempts.count : 'N/A'}
  `;
}

function connectionSummary(chat, index) {
  const duration = chat.endTime ? chat.endTime - chat.connectionStartTime : 'N/A';
  const messageCount = chat.messages.length;
  const errors = chat.messages.filter(m => m.type === 'error').length;

  let summary = `
Connection ${index + 1} (${chat.id}):
  Duration: ${duration === 'N/A' ? 'N/A' : duration + 'ms'}
  Connection Time: ${chat.connectionTime || 'N/A'}ms
  Messages Exchanged: ${messageCount}
  Errors: ${errors}
  `;

  if (messageCount > 0) {
    const responseTimes = [];
    let lastSentTimestamp = null;

    chat.messages.forEach((message, i) => {
      if (message.type === 'received' && lastSentTimestamp) {
        responseTimes.push(message.timestamp - lastSentTimestamp);
      } else if (message.type === 'sent') {
        lastSentTimestamp = message.timestamp;
      }
    });

    if (responseTimes.length > 0) {
      const avgResponseTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;
      summary += `  Average Response Time: ${avgResponseTime.toFixed(2)}ms\n`;
    }
  }

  return summary;
}