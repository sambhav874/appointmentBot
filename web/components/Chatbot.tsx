'use client'
import { useState, useRef, useEffect } from 'react';
import { IoMdSend } from 'react-icons/io';
import { IoClose } from 'react-icons/io5';
import { FaRobot } from 'react-icons/fa';
import { motion, AnimatePresence } from 'framer-motion';
import { FaCalendarAlt, FaClock } from 'react-icons/fa';

interface Message {
  id: string;
  text: string;
  isBot: boolean;
  timestamp: Date;
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showTimePicker, setShowTimePicker] = useState(false);
  const [showInsuranceTypes, setShowInsuranceTypes] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const insuranceTypes = [
    "Health Insurance",
    "Life Insurance", 
    "Auto Insurance",
    "Home Insurance",
    "Travel Insurance",
    "Business Insurance"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      isBot: false,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5005/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputText,
          action: 'chat'
        }),
      });

      const data = await response.json();
      
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response,
        isBot: true,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDateSelect = (date: string) => {
    setInputText(date);
    setShowDatePicker(false);
  };

  const handleTimeSelect = (time: string) => {
    setInputText(time);
    setShowTimePicker(false);
  };

  const handleInsuranceSelect = (type: string) => {
    setInputText(type);
    setShowInsuranceTypes(false);
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="bg-white rounded-lg shadow-xl w-96 h-[600px] flex flex-col"
          >
            {/* Header */}
            <div className="bg-blue-600 text-white p-4 rounded-t-lg flex justify-between items-center">
              <div className="flex items-center gap-2">
                <FaRobot className="text-xl" />
                <h3 className="font-semibold">Insurance Assistant</h3>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-white hover:text-gray-200 transition-colors"
              >
                <IoClose className="text-xl" />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.isBot ? 'justify-start' : 'justify-end'}`}
                >
                  <div
                    className={`max-w-[80%] p-3 rounded-lg ${
                      message.isBot
                        ? 'bg-gray-100 text-gray-800'
                        : 'bg-blue-600 text-white'
                    }`}
                  >
                    <p className="text-sm">{message.text}</p>
                    <span className="text-xs opacity-70 mt-1 block">
                      {message.timestamp.toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg p-3">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t">
              <div className="flex gap-2 mb-2">
                <button
                  onClick={() => setShowDatePicker(!showDatePicker)}
                  className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                >
                  <FaCalendarAlt className="text-xl" />
                </button>
                <button
                  onClick={() => setShowTimePicker(!showTimePicker)}
                  className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                >
                  <FaClock className="text-xl" />
                </button>
                <button
                  onClick={() => setShowInsuranceTypes(!showInsuranceTypes)}
                  className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                >
                  Insurance Types
                </button>
              </div>

              {showDatePicker && (
                <div className="mb-2 p-2 bg-white border rounded-lg shadow-lg">
                  <input 
                    type="date"
                    onChange={(e) => handleDateSelect(e.target.value)}
                    className="w-full p-2 border rounded"
                  />
                </div>
              )}

              {showTimePicker && (
                <div className="mb-2 p-2 bg-white border rounded-lg shadow-lg">
                  <input 
                    type="time"
                    onChange={(e) => handleTimeSelect(e.target.value)}
                    className="w-full p-2 border rounded"
                  />
                </div>
              )}

              {showInsuranceTypes && (
                <div className="mb-2 p-2 bg-white border rounded-lg shadow-lg">
                  {insuranceTypes.map((type) => (
                    <button
                      key={type}
                      onClick={() => handleInsuranceSelect(type)}
                      className="block w-full text-left p-2 hover:bg-blue-50 rounded"
                    >
                      {type}
                    </button>
                  ))}
                </div>
              )}

              <div className="flex gap-2">
                <input
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Type your message..."
                  className="flex-1 p-2 border rounded-lg focus:outline-none focus:border-blue-600"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!inputText.trim() || isLoading}
                  className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <IoMdSend className="text-xl" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Toggle Button */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setIsOpen(!isOpen)}
        className="bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition-colors"
      >
        <FaRobot className="text-2xl" />
      </motion.button>
    </div>
  );
}