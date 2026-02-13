import React from 'react';
import '../styles/Hero.css';

function Hero({ icon, title, subtitle, className = '' }) {
  return (
    <div className={`page-hero ${className}`}>
      <div className="page-hero__icon">{icon}</div>
      <h1>{title}</h1>
      {subtitle && <p className="page-hero__subtitle">{subtitle}</p>}
    </div>
  );
}

export default Hero;
