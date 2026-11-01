import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import '../../styles/Header.css';

export const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="app-header">
      <div className="header-content">
        <h1>Graphene Trace</h1>
        <div className="header-right">
          <span className="user-info">
            {user?.photo_url && (
              <img src={user.photo_url} alt="" className="header-avatar" />
            )}
            {user?.name} ({user?.role})
          </span>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </div>
      </div>
    </header>
  );
};
