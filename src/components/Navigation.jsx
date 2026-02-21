import React, { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { Leaf, LogOut, ChevronDown } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import '../styles/Navigation.css';

function Navigation() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const { isAuthenticated, user, logout, setShowAuthModal } = useAuth();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLogout = () => {
    logout();
    setShowUserMenu(false);
  };

  return (
    <nav className={`navbar ${isScrolled ? 'scrolled' : ''}`}>
      <div className="nav-container">
        <NavLink to="/" className="nav-logo">
          <span className="logo-icon">
            <Leaf size={20} />
          </span>
          Smart Farming Assistant
        </NavLink>
        <ul className="nav-menu">
          <li className="nav-item">
            <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              Home
            </NavLink>
          </li>
          {isAuthenticated && (
            <>
              <li className="nav-item">
                <NavLink to="/yield" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  Irrigation Planning
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink to="/crop-management" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  Crop Management
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink to="/calendar" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  Calendar
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink to="/irrigation" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  Irrigation Status
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink to="/dashboard" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                  Dashboard
                </NavLink>
              </li>
            </>
          )}
          <li className="nav-item">
            <NavLink to="/weather" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              Weather
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink to="/chatbot" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              Chatbot
            </NavLink>
          </li>
        </ul>

        {/* Auth Section */}
        <div className="nav-auth">
          {isAuthenticated ? (
            <div className="nav-user-menu">
              <button
                className="nav-user-button"
                onClick={() => setShowUserMenu(!showUserMenu)}
              >
                <span className="nav-user-avatar">{user.username.charAt(0).toUpperCase()}</span>
                <span className="nav-user-name">{user.username}</span>
                <ChevronDown size={16} className={showUserMenu ? 'rotate' : ''} />
              </button>

              {showUserMenu && (
                <div className="nav-user-dropdown">
                  <div className="nav-user-info">
                    <p className="nav-user-email">{user.email}</p>
                  </div>
                  <button
                    className="nav-logout-button"
                    onClick={handleLogout}
                  >
                    <LogOut size={16} />
                    Logout
                  </button>
                </div>
              )}
            </div>
          ) : (
            <button
              className="nav-signin-button"
              onClick={() => setShowAuthModal(true)}
            >
              Sign In
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navigation;
