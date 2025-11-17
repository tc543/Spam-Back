import React from 'react';
import './StatsCard.css';

function StatsCard({ title, value }) {
  return (
    <div className="stats-card">
      <p className="stats-title">{title}</p>
      <p className="stats-value">{value}</p>
    </div>
  );
}

export default StatsCard;
