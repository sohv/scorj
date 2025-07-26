import React, { useState } from 'react';
import axios from 'axios';

interface AIChatProps {
  apiBaseUrl: string;
  context?: string;
}

const AIChat: React.FC<AIChatProps> = ({ apiBaseUrl, context }) => {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setError(null);
    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    try {
      const response = await axios.post(`${apiBaseUrl}/ai/chat`, new URLSearchParams({
        question: input,
        context: context || '',
      }), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      setMessages((prev) => [...prev, { role: 'ai', content: response.data.response }]);
    } catch (err: any) {
      setError('Failed to get AI response.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ai-chat-container">
      <h3>AI Chat Assistant</h3>
      <div className="chat-history">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.role}`}>
            <strong>{msg.role === 'user' ? 'You' : 'AI'}:</strong> {msg.content}
          </div>
        ))}
      </div>
      {error && <div className="chat-error">{error}</div>}
      <div className="chat-input-row">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask anything about your resume or job..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()}>
          {loading ? 'Thinking...' : 'Send'}
        </button>
      </div>
    </div>
  );
};

export default AIChat;
