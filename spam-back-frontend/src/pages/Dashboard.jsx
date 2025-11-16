import React from 'react';
import StatsCard from '../components/StatsCard';
import './Dashboard.css';

function Dashboard() {
  return (
    <div className="dashboard">
      <h2>Dashboard</h2>
      <div className="stats-container">
        <StatsCard title="Active Spammers" value="12" />
        <StatsCard title="Messages Sent" value="348" />
        <StatsCard title="Avg Response Time" value="2m 15s" />
      </div>
    </div>
  );
}

export default Dashboard;
