import React from 'react';
import ConversationList from '../components/ConversationList';
import './Conversations.css';

const dummyMessages = [
  { text: "Hello! Buy our product", fromUser: false },
  { text: "Stop spamming me", fromUser: true },
  { text: "Limited offer just for you!", fromUser: false },
];

function Conversations() {
  return (
    <div className="conversations-page">
      <h2>Conversations</h2>
      <ConversationList messages={dummyMessages} />
    </div>
  );
}

export default Conversations;
