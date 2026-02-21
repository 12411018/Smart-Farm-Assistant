import React, { useState, useEffect } from 'react';
import { MessageSquarePlus, Trash2, MessageSquare, Clock } from 'lucide-react';
import '../styles/ChatHistory.css';

function ChatHistory({ 
  onSelectConversation, 
  onNewConversation, 
  currentConversationId,
  userId = "default_user",
  refreshTrigger = 0
}) {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_BASE = `${window.location.protocol}//${window.location.hostname}:8000`;

  // Load conversations on mount and when refreshTrigger changes
  useEffect(() => {
    loadConversations();
  }, [userId, refreshTrigger]);

  const loadConversations = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/conversations?user_id=${userId}`);
      
      if (!response.ok) {
        throw new Error('Failed to load conversations');
      }
      
      const data = await response.json();
      setConversations(data);
      setError(null);
    } catch (err) {
      console.error('Error loading conversations:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleNewConversation = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/conversations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          title: 'New Conversation'
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create conversation');
      }

      const newConv = await response.json();
      setConversations([newConv, ...conversations]);
      onNewConversation(newConv.id);
    } catch (err) {
      console.error('Error creating conversation:', err);
    }
  };

  const handleDeleteConversation = async (conversationId, event) => {
    event.stopPropagation(); // Prevent selecting the conversation
    
    if (!window.confirm('Delete this conversation?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/conversations/${conversationId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error('Failed to delete conversation');
      }

      setConversations(conversations.filter(c => c.id !== conversationId));
      
      // If deleted conversation was active, trigger new conversation
      if (conversationId === currentConversationId) {
        onNewConversation(null);
      }
    } catch (err) {
      console.error('Error deleting conversation:', err);
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="chat-history">
        <div className="chat-history-header">
          <h2>Chat History</h2>
        </div>
        <div className="chat-history-loading">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-history">
      <div className="chat-history-header">
        <h2>Chats</h2>
        <button 
          className="new-chat-btn" 
          onClick={handleNewConversation}
          title="New Conversation"
        >
          <MessageSquarePlus size={20} />
        </button>
      </div>

      {error && (
        <div className="chat-history-error">
          <p>Error: {error}</p>
          <button onClick={loadConversations} className="retry-btn">
            Retry
          </button>
        </div>
      )}

      <div className="conversations-list">
        {conversations.length === 0 ? (
          <div className="empty-state">
            <MessageSquare size={48} />
            <p>No conversations yet</p>
            <button onClick={handleNewConversation} className="start-chat-btn">
              Start a chat
            </button>
          </div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              className={`conversation-item ${conv.id === currentConversationId ? 'active' : ''}`}
              onClick={() => onSelectConversation(conv.id)}
            >
              <div className="conversation-content">
                <div className="conversation-header">
                  <h3 className="conversation-title">{conv.title}</h3>
                  <button
                    className="delete-btn"
                    onClick={(e) => handleDeleteConversation(conv.id, e)}
                    title="Delete conversation"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
                <div className="conversation-meta">
                  <span className="message-count">
                    {conv.message_count} message{conv.message_count !== 1 ? 's' : ''}
                  </span>
                  <span className="conversation-time">
                    <Clock size={12} />
                    {formatTimestamp(conv.updated_at)}
                  </span>
                </div>
                {conv.last_message && (
                  <p className="conversation-preview">
                    {conv.last_message.substring(0, 60)}
                    {conv.last_message.length > 60 ? '...' : ''}
                  </p>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default ChatHistory;
