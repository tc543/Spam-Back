import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Sidebar.css';

function Sidebar() {
  const location = useLocation();

  return (
    <div className="sidebar">
      <h2 className="sidebar-title">Spam Back!</h2>
      <nav className="sidebar-nav">
        <Link className={location.pathname === '/' ? 'active' : ''} to="/">Dashboard</Link>
        <Link className={location.pathname === '/conversations' ? 'active' : ''} to="/conversations">Conversations</Link>
        <Link className={location.pathname === '/settings' ? 'active' : ''} to="/settings">Settings</Link>
      </nav>
    </div>
  );
}

export default Sidebar;
