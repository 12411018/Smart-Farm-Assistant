import React, { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { Leaf } from 'lucide-react';
import '../styles/Navigation.css';

function Navigation() {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

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
      </div>
    </nav>
  );
}

export default Navigation;
