import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// Configuration constants
const BASE_URL = 'http://localhost:5005/chat';
const TEST_DURATION = '15s';
const VIRTUAL_USERS = 10;

// Custom metrics
const successRate = new Rate('success_rate');
const responseTimes = new Trend('response_times');
const appointmentRate = new Rate('appointment_rate');

// Test configuration
export const options = {
  vus: VIRTUAL_USERS,
  duration: TEST_DURATION,
};

// Questions
const INSURANCE_QUESTIONS = [
  "What types of insurance do you offer?",
  "How much does health insurance cost?",
  "Can I get a quote for auto insurance?",
  "What's covered under home insurance?",
  "Do you offer life insurance policies?",
  "How do I file an insurance claim?",
  "What factors affect my insurance premium?",
  "Is travel insurance worth it?",
  "Can I bundle different types of insurance?",
  "What's the difference between term and whole life insurance?",
];

const IRRELEVANT_QUESTIONS = [
  "What's the weather like today?",
  "Can you recommend a good restaurant?",
  "How do I bake a cake?",
  "What's the capital of France?",
  "Who won the last World Cup?",
  "How tall is Mount Everest?",
  "What's the plot of the latest Marvel movie?",
  "How do I learn to play guitar?",
  "What's the best way to lose weight?",
  "Can you tell me a joke?",
];

// Escape CSV fields
function escapeCSV(field) {
  if (field === null || field === undefined) return '';
  const escaped = String(field).replace(/"/g, '""');
  return escaped.includes(',') || escaped.includes('"') || escaped.includes('\n')
    ? `"${escaped}"`
    : escaped;
}

// Parse chatbot response
function parseResponse(body) {
  try {
    const data = JSON.parse(body);
    return {
      response: data.response || '',
      intent: data.intent || '',
      appointmentScheduled: !!data.appointment_scheduled
    };
  } catch (error) {
    console.error('Response parsing error:', error);
    return {
      response: '',
      intent: '',
      appointmentScheduled: false
    };
  }
}

// Main test scenario
export default function () {
  // Determine question type
  const isInsuranceQuestion = Math.random() < 0.7;
  const question = isInsuranceQuestion
    ? randomItem(INSURANCE_QUESTIONS)
    : randomItem(IRRELEVANT_QUESTIONS);

  const payload = JSON.stringify({ message: question });
  const params = {
    headers: { 'Content-Type': 'application/json' }
  };

  // Perform HTTP request
  const response = http.post(BASE_URL, payload, params);

  // Validate response
  const success = check(response, {
    'status is 200': r => r.status === 200,
    'response has content': r => r.body && r.body.length > 0
  });

  // Parse response details
  const parsedResponse = parseResponse(response.body || '{}');

  // Update metrics
  successRate.add(success);
  responseTimes.add(response.timings.duration);
  appointmentRate.add(parsedResponse.appointmentScheduled);

  // Simulate user think time
  sleep(Math.random() * 3 + 2);
}

// Summary handler
export function handleSummary(data) {
  // Prepare CSV content
  let csvContent = 'Timestamp,Question,Question Type,Response,Intent,Appointment Scheduled,Response Time (ms),Success\n';
  
  // Collect metrics data
  csvContent += Object.entries(data.metrics).map(([key, metric]) => {
    return `${key},${metric.value || 0}`;
  }).join('\n');

  return {
    'chatbot_test_metrics.csv': csvContent
  };
}