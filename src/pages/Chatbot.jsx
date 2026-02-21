import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, CloudSun, Droplets, Leaf, LineChart, Mic, Send, Volume2 } from 'lucide-react';
import '../styles/Chatbot.css';

const API_BASE = import.meta.env.VITE_API_BASE_URL || `http://${window.location.hostname}:8000`;

function Chatbot() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: 'Hello! I am your Smart Farming Assistant. How can I help you today?',
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [hasVoiceSupport, setHasVoiceSupport] = useState(true);
  const chatContainerRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    if (!chatContainerRef.current) return;
    const container = chatContainerRef.current;
    const id = requestAnimationFrame(() => {
      container.scrollTop = container.scrollHeight;
    });
    return () => cancelAnimationFrame(id);
  }, [messages, isLoading]);

  // Set up browser speech recognition once (Web Speech API).
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition || window.mozSpeechRecognition;

    if (!SpeechRecognition) {
      setHasVoiceSupport(false);
      return undefined;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onerror = (event) => {
      console.error('Voice input error:', event.error);
      setIsListening(false);
    };
    recognition.onresult = (event) => {
      let finalTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        }
      }
      if (!finalTranscript) return;
      // Only append final results to avoid duplicate interim text.
      setInputValue((prev) => `${prev} ${finalTranscript}`.trim());
    };

    recognitionRef.current = recognition;
    setHasVoiceSupport(true);

    return () => {
      recognition.stop();
    };
  }, []);

  const handleToggleMic = () => {
    if (!hasVoiceSupport) return;
    const recognition = recognitionRef.current;
    if (!recognition) return;

    if (isListening) {
      recognition.stop();
    } else {
      try {
        recognition.start();
      } catch (err) {
        console.error('Failed to start voice input:', err);
      }
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (inputValue.trim() === '') return;

    // Add user message
    const userMessage = {
      id: messages.length + 1,
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Build rich context from farm data
      const context = `
📍 Location: Pune, Maharashtra, India
🌡️ Current Weather: Clear sky, Temperature 23°C, Humidity 37%
💧 Soil Moisture: Medium (45%)
🌾 Active Crop: Wheat
📊 Growth Stage: Vegetative phase (32 days)
🌧️ Rainfall Status: No rain expected in next 24 hours
💰 Budget: Medium-scale farm`;

      // Call FastAPI backend using environment variable
      const backendUrl = `${API_BASE}/chat`;
      console.log('Sending request to:', backendUrl);
      console.log('Message:', inputValue);
      
      const response = await fetch(backendUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue,
          context: context,
          language: 'en',
        }),
      });

      console.log('Response status:', response.status);
      
      if (!response.ok) {
        console.error('Backend returned error:', response.status, response.statusText);
        throw new Error(`Backend error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Backend response:', data);

      const botMessage = {
        id: messages.length + 2,
        text: data.reply || data.error || 'Unable to get response. Please check backend.',
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat error:', error.message);
      const errorMessage = {
        id: messages.length + 2,
        text: `Connection error: ${error.message}. Make sure FastAPI backend is running on ${API_BASE}`,
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbot-page">
      <div className="chatbot-container">
        <div className="chatbot-header">
          <div className="header-icon">
            <Bot size={28} />
          </div>
          <div>
            <h1>Smart Farming Chatbot</h1>
            <p>Ask about crop management, irrigation, or yield strategy.</p>
          </div>
        </div>

        <div className="chat-box">
          <div className="messages-container" ref={chatContainerRef}>
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.sender}`}>
                <div className="message-bubble">
                  <ReactMarkdown>{message.text}</ReactMarkdown>
                  <span className="message-time">
                    {message.timestamp.toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message bot">
                <div className="message-bubble">
                  <p>Thinking...</p>
                  <span className="message-time">
                    {new Date().toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                </div>
              </div>
            )}
          </div>

          <form onSubmit={handleSendMessage} className="chat-input-form">
            <div className="input-wrapper">
              <button
                type="button"
                className={`icon-btn ${isListening ? 'listening' : ''}`}
                title={hasVoiceSupport ? 'Start voice input' : 'Voice input not supported'}
                onClick={handleToggleMic}
                disabled={!hasVoiceSupport || isLoading}
              >
                <Mic size={18} />
              </button>
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Type your question..."
                className="chat-input"
              />
              <button
                type="button"
                className="icon-btn"
                title="Voice response (UI only)"
              >
                <Volume2 size={18} />
              </button>
              <button type="submit" className="send-btn" disabled={isLoading}>
                <Send size={16} /> {isLoading ? 'Loading...' : 'Send'}
              </button>
            </div>
          </form>
        </div>

        <div className="quick-tips">
          <h3>Quick Tips</h3>
          <div className="tips-grid">
            <div className="tip-card">
              <span className="tip-icon">
                <Droplets size={18} />
              </span>
              <p>Ask about irrigation schedules</p>
            </div>
            <div className="tip-card">
              <span className="tip-icon">
                <Leaf size={18} />
              </span>
              <p>Try crop seek: "Which crop for sandy soil?"</p>
            </div>
            <div className="tip-card">
              <span className="tip-icon">
                <Leaf size={18} />
              </span>
              <p>Get crop growth recommendations</p>
            </div>
            <div className="tip-card">
              <span className="tip-icon">
                <CloudSun size={18} />
              </span>
              <p>Weather-based farming advice</p>
            </div>
            <div className="tip-card">
              <span className="tip-icon">
                <LineChart size={18} />
              </span>
              <p>Yield optimization tips</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Chatbot;
