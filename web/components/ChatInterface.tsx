'use client'

import React, { useState, useEffect, useRef } from 'react';
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Sparkles, MessageCircle, Send, Smile, X } from 'lucide-react'

interface Message {
  text: string;
  isUser: boolean;
  timestamp?: Date;
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [sentimentAnalysis, setSentimentAnalysis] = useState<any>(null);
  const [isCollectingAppointmentDetails, setIsCollectingAppointmentDetails] = useState(false);
  const [appointmentDetails, setAppointmentDetails] = useState({
    name: '',
    email: '',
    mobile: '',
    insurance_type: '',
    preferred_date: '',
    preferred_time: '',
  });
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (message: string) => {
    if (!message.trim()) return;

    const newMessages = [...messages, { text: message, isUser: true, timestamp: new Date() }];
    setMessages(newMessages);
    setInput('');

    try {
      const response = await fetch('http://localhost:5005/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message }),
      });

      const data = await response.json();
      const botMessage = { text: data.response, isUser: false, timestamp: new Date() };
      setMessages([...newMessages, botMessage]);

      if (data.response.includes("Would you like to schedule an appointment?")) {
        setIsCollectingAppointmentDetails(true);
        setMessages(prev => [...prev, { 
          text: "Great! Let's schedule your appointment. Please provide your full name.", 
          isUser: false, 
          timestamp: new Date() 
        }]);
      } else if (isCollectingAppointmentDetails) {
        handleAppointmentDetails(message);
      }

      if (data.intent === 'farewell') {
        const sentimentResponse = await fetch('http://localhost:5005/sentiment_analysis');
        const sentimentData = await sentimentResponse.json();
        setSentimentAnalysis(sentimentData);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleAppointmentDetails = (message: string) => {
    if (!appointmentDetails.name) {
      setAppointmentDetails(prev => ({ ...prev, name: message }));
      setMessages(prev => [...prev, { 
        text: "Thank you. Now, please provide your email address.", 
        isUser: false, 
        timestamp: new Date() 
      }]);
    } else if (!appointmentDetails.email) {
      setAppointmentDetails(prev => ({ ...prev, email: message }));
      setMessages(prev => [...prev, { 
        text: "Great. What's your mobile number?", 
        isUser: false, 
        timestamp: new Date() 
      }]);
    } else if (!appointmentDetails.mobile) {
      setAppointmentDetails(prev => ({ ...prev, mobile: message }));
      setMessages(prev => [...prev, { 
        text: "What type of insurance are you interested in? (health/life/auto/home)", 
        isUser: false, 
        timestamp: new Date() 
      }]);
    } else if (!appointmentDetails.insurance_type) {
      setAppointmentDetails(prev => ({ ...prev, insurance_type: message }));
      setMessages(prev => [...prev, { 
        text: "What's your preferred date for the appointment? (YYYY-MM-DD)", 
        isUser: false, 
        timestamp: new Date() 
      }]);
    } else if (!appointmentDetails.preferred_date) {
      setAppointmentDetails(prev => ({ ...prev, preferred_date: message }));
      setMessages(prev => [...prev, { 
        text: "And what time would you prefer? (HH:MM)", 
        isUser: false, 
        timestamp: new Date() 
      }]);
    } else if (!appointmentDetails.preferred_time) {
      setAppointmentDetails(prev => ({ ...prev, preferred_time: message }));
      setIsCollectingAppointmentDetails(false);
      sendMessage(JSON.stringify(appointmentDetails));
    }
  };

  const clearChat = () => {
    setMessages([]);
    setSentimentAnalysis(null);
    setIsCollectingAppointmentDetails(false);
    setAppointmentDetails({
      name: '',
      email: '',
      mobile: '',
      insurance_type: '',
      preferred_date: '',
      preferred_time: '',
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl shadow-2xl border-2 border-blue-200/50">
        <CardHeader className="bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-t-xl">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <MessageCircle className="w-8 h-8" />
              <CardTitle className="text-xl font-bold">Insurance Companion</CardTitle>
            </div>
            <Button 
              variant="ghost" 
              size="icon" 
              className="text-white hover:bg-white/20"
              onClick={clearChat}
            >
              <X className="w-6 h-6" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="h-[500px] overflow-y-auto bg-white/80 backdrop-blur-sm">
          {messages.map((message, index) => (
            <div 
              key={index} 
              className={`mb-4 flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
            >
              <div 
                className={`max-w-[80%] p-3 rounded-2xl shadow-md ${
                  message.isUser 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <p className="text-sm">{message.text}</p>
                <div className="text-xs opacity-60 mt-1 text-right">
                  {message.timestamp?.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                </div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </CardContent>
        <CardFooter className="bg-white/50 backdrop-blur-sm rounded-b-xl">
          <div className="flex w-full space-x-2">
            <Input
              type="text"
              placeholder="Type your message..."
              value={input}
              className="flex-grow rounded-full"
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage(input)}
            />
            <Button 
              onClick={() => sendMessage(input)} 
              className="rounded-full"
              disabled={!input.trim()}
            >
              <Send className="w-5 h-5 mr-2" /> Send
            </Button>
          </div>
        </CardFooter>
        {sentimentAnalysis && (
          <CardFooter className="bg-gradient-to-r from-blue-100 to-purple-100 rounded-b-xl">
            <div className="w-full flex items-center justify-between p-3">
              <div className="flex items-center space-x-2">
                <Smile className="w-6 h-6 text-blue-600" />
                <h3 className="font-bold text-blue-800">Conversation Sentiment</h3>
              </div>
              <div className="flex space-x-4">
                <div className="text-center">
                  <p className="text-green-600 font-bold">{sentimentAnalysis.percentages.positive.toFixed(2)}%</p>
                  <p className="text-xs text-green-500">Positive</p>
                </div>
                <div className="text-center">
                  <p className="text-gray-600 font-bold">{sentimentAnalysis.percentages.neutral.toFixed(2)}%</p>
                  <p className="text-xs text-gray-500">Neutral</p>
                </div>
                <div className="text-center">
                  <p className="text-red-600 font-bold">{sentimentAnalysis.percentages.negative.toFixed(2)}%</p>
                  <p className="text-xs text-red-500">Negative</p>
                </div>
              </div>
            </div>
          </CardFooter>
        )}
      </Card>
    </div>
  );
}