/**
 * Enhanced Chatbot Component with Chat History Integration
 * 
 * MERGE NOTE: This version includes local enhancements not in GitHub repo:
 * - ChatHistory sidebar (new component)
 * - User persistence via localStorage (getUserId)
 * - Voice recognition with Web Speech API
 * - ReactMarkdown rendering
 * - Auto-retry on network errors
 * - Smooth loading transitions
 * 
 * These enhancements are backward compatible with GitHub version.
 * Keep this version during merge - it's superior.
 */
import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, CloudSun, Droplets, Leaf, LineChart, Mic, Send, Volume2 } from 'lucide-react';
import ChatHistory from '../components/ChatHistory'; // NEW: Not in GitHub version
import '../styles/Chatbot.css';

// NEW FEATURE: Get or create a unique user ID that persists across sessions
function getUserId() {
  let userId = localStorage.getItem('smart_farm_user_id');
  if (!userId) {
    // Generate a unique ID: timestamp + random string
    userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('smart_farm_user_id', userId);
    console.log('Created new user ID:', userId);
  } else {
    console.log('Retrieved existing user ID:', userId);
  }
  return userId;
}

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
  const [isLoadingConversation, setIsLoadingConversation] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [hasVoiceSupport, setHasVoiceSupport] = useState(true);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [userId] = useState(getUserId()); // Persistent user ID from localStorage
  const [refreshHistory, setRefreshHistory] = useState(0);
  const chatContainerRef = useRef(null);
  const recognitionRef = useRef(null);
  const isManualStopRef = useRef(false);

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
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    
    let finalTranscript = '';

    recognition.onstart = () => {
      console.log('✓ Microphone is ON - speak your question');
      finalTranscript = '';
      setIsListening(true);
    };
    
    recognition.onend = () => {
      console.log('✓ Microphone stopped');
      setIsListening(false);
      
      // Add captured text to input
      if (finalTranscript.trim()) {
        setInputValue((prev) => (prev ? `${prev} ${finalTranscript}` : finalTranscript).trim());
        console.log('✓ Added:', finalTranscript.trim());
      } else {
        console.log('⚠ No speech captured');
      }
    };
    
    recognition.onerror = (event) => {
      console.error('Voice error:', event.error);
      
      // Handle specific errors
      if (event.error === 'not-allowed') {
        setIsListening(false);
        alert('Microphone access denied. Please allow microphone access in your browser settings.');
      } else if (event.error === 'no-speech') {
        console.log('⚠ No speech detected');
        // Don't stop - might just be a pause
      } else if (event.error === 'audio-capture') {
        setIsListening(false);
        alert('No microphone found. Please check your microphone connection.');
      } else if (event.error === 'network') {
        console.warn('⚠ Network error - auto-retrying...');
        // Auto-retry on network error if not manually stopped
        if (!isManualStopRef.current) {
          setTimeout(() => {
            try {
              recognition.start();
              console.log('↻ Retried successfully');
            } catch (e) {
              console.log('Retry failed:', e.message);
              setIsListening(false);
            }
          }, 100);
        } else {
          setIsListening(false);
        }
      } else if (event.error === 'aborted') {
        console.log('Recognition aborted');
        setIsListening(false);
      } else {
        console.error('Recognition error:', event.error);
      }
    };
    recognition.onresult = (event) => {
      let interimText = '';
      
      for (let i = 0; i < event.results.length; i += 1) {
        const transcript = event.results[i][0].transcript;
        
        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' ';
          console.log('✓ Heard:', transcript);
        } else {
          interimText += transcript;
        }
      }
      
      // Show interim results in console
      if (interimText) {
        console.log('🎤 Listening:', interimText);
      }
    };

    recognitionRef.current = recognition;
    setHasVoiceSupport(true);

    return () => {
      try {
        recognition.stop();
      } catch (e) {
        // Ignore errors on cleanup
      }
    };
  }, []);

  const handleToggleMic = () => {
    if (!hasVoiceSupport) {
      alert('Voice input is not supported in your browser. Please use Chrome, Edge, or Safari.');
      return;
    }
    
    const recognition = recognitionRef.current;
    if (!recognition) {
      alert('Voice recognition not initialized. Please refresh the page.');
      return;
    }

    if (isListening) {
      console.log('Manually stopping recognition...');
      isManualStopRef.current = true;
      recognition.stop();
      setTimeout(() => {
        isManualStopRef.current = false;
      }, 500);
    } else {
      console.log('Starting voice recognition - speak immediately!');
      isManualStopRef.current = false;
      try {
        recognition.start();
      } catch (err) {
        console.error('Failed to start voice input:', err);
        
        // Provide helpful error messages
        if (err.name === 'NotAllowedError') {
          alert('Microphone access denied. Please enable microphone permissions in your browser settings.');
        } else if (err.name === 'NotFoundError') {
          alert('No microphone found. Please connect a microphone and try again.');
        } else if (err.message.includes('already started')) {
          // Recognition already running, try to stop and restart
          recognition.stop();
          setTimeout(() => {
            try {
              recognition.start();
            } catch (retryErr) {
              alert('Could not start voice recognition. Please try again.');
            }
          }, 100);
        } else {
          alert(`Voice input error: ${err.message || 'Unknown error'}. Make sure you're using HTTPS or localhost.`);
        }
      }
    }
  };

  const handleSelectConversation = async (conversationId) => {
    try {
      setIsLoadingConversation(true);
      const backendUrl = `${window.location.protocol}//${window.location.hostname}:8000`;
      const response = await fetch(`${backendUrl}/api/conversations/${conversationId}`);
      
      if (!response.ok) {
        throw new Error('Failed to load conversation');
      }
      
      const data = await response.json();
      
      // Small delay for smooth transition
      await new Promise(resolve => setTimeout(resolve, 150));
      
      // Convert messages to UI format
      const loadedMessages = data.messages.map((msg, index) => ({
        id: index + 1,
        text: msg.content,
        sender: msg.role,
        timestamp: new Date(msg.timestamp),
      }));
      
      setMessages(loadedMessages);
      setCurrentConversationId(conversationId);
    } catch (error) {
      console.error('Error loading conversation:', error);
    } finally {
      setIsLoadingConversation(false);
    }
  };

  const handleNewConversation = (conversationId) => {
    // Reset to welcome message
    setMessages([
      {
        id: 1,
        text: 'Hello! I am your Smart Farming Assistant. How can I help you today?',
        sender: 'bot',
        timestamp: new Date(),
      },
    ]);
    setCurrentConversationId(conversationId);
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

      // Call FastAPI backend (match current host, port 8000)
      const backendUrl = `${window.location.protocol}//${window.location.hostname}:8000/chat`;
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
          conversation_id: currentConversationId,
          user_id: userId,
        }),
      });

      console.log('Response status:', response.status);
      
      if (!response.ok) {
        console.error('Backend returned error:', response.status, response.statusText);
        throw new Error(`Backend error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Backend response:', data);

      // Update conversation ID if new conversation was created
      if (data.conversation_id && data.conversation_id !== currentConversationId) {
        setCurrentConversationId(data.conversation_id);
      }
      
      // Always refresh chat history to update titles and message counts
      setRefreshHistory(prev => prev + 1);

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
        text: `Connection error: ${error.message}. Make sure FastAPI backend is running on http://127.0.0.1:8000`,
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
      <div className="chatbot-layout">
        <ChatHistory 
          onSelectConversation={handleSelectConversation}
          onNewConversation={handleNewConversation}
          currentConversationId={currentConversationId}
          userId={userId}
          refreshTrigger={refreshHistory}
        />
        
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
          <div className={`messages-container ${isLoadingConversation ? 'loading' : ''}`} ref={chatContainerRef}>
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
                title={
                  !hasVoiceSupport
                    ? 'Voice input not supported'
                    : isListening
                    ? '🎤 Recording... Click again to stop'
                    : 'Click to start voice input'
                }
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
    </div>
  );
}

export default Chatbot;
