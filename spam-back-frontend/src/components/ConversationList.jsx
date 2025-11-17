import React from 'react';
import MessageBubble from './MessageBubble';
import './ConversationList.css';

function ConversationList({ messages }) {
  return (
    <div className="conversation-list">
      {messages.map((msg, idx) => (
        <MessageBubble key={idx} message={msg.text} fromUser={msg.fromUser} />
      ))}
    </div>
  );
}

export default ConversationList;
