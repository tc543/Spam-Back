import React from 'react';
import './MessageBubble.css';

function MessageBubble({ message, fromUser }) {
  return (
    <div className={`message-bubble ${fromUser ? 'user' : 'spam'}`}>
      {message}
    </div>
  );
}

export default MessageBubble;
