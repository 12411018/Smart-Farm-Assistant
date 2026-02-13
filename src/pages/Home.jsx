import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Bot, Droplets, LayoutDashboard, LineChart } from 'lucide-react';
import '../styles/Home.css';

function Home() {
  const cards = [
    {
      id: 1,
      title: 'Yield Intelligence',
      description: 'Capture crop performance and track profitability in one place.',
      Icon: LineChart,
      link: '/yield',
    },
    {
      id: 2,
      title: 'Smart Irrigation Planning',
      description: 'Schedule water precisely with stage-aware recommendations.',
      Icon: Droplets,
      link: '/irrigation',
    },
    {
      id: 3,
      title: 'AI Farming Chatbot',
      description: 'Ask questions and get instant agronomy guidance.',
      Icon: Bot,
      link: '/chatbot',
    },
    {
      id: 4,
      title: 'Real-Time Farm Dashboard',
      description: 'Monitor soil, climate, and yield signals in real time.',
      Icon: LayoutDashboard,
      link: '/dashboard',
    },
  ];

  return (
    <div className="home">
      <section className="hero">
        <div className="hero-overlay"></div>
        <div className="hero-content container">
          <div className="hero-grid">
            <div className="hero-text">
              <span className="hero-eyebrow">Agri-tech intelligence platform</span>
              <h1>Smart Farming Assistant</h1>
              <p className="hero-subtitle">
                AI-powered crop planning, irrigation & yield optimization
              </p>
              <p className="hero-description">
                Designed for high-impact farms and climate-ready decision making. Monitor
                performance, plan irrigation, and unlock smarter yields in one premium
                workspace.
              </p>
              <div className="hero-ctas">
                <Link to="/yield" className="btn btn-primary">
                  Get Started <ArrowRight size={18} />
                </Link>
                <Link to="/dashboard" className="btn btn-secondary">
                  View Dashboard
                </Link>
              </div>
              <div className="hero-stats">
                <div>
                  <h3>18%</h3>
                  <p>Yield uplift potential</p>
                </div>
                <div>
                  <h3>32%</h3>
                  <p>Water efficiency gain</p>
                </div>
                <div>
                  <h3>120+</h3>
                  <p>Active field sensors</p>
                </div>
              </div>
            </div>
            <div className="hero-panel">
              <div className="card hero-card glass-card">
                <div className="hero-card-header">
                  <span className="icon-badge">
                    <LineChart size={20} />
                  </span>
                  <div>
                    <p className="card-eyebrow">This week</p>
                    <h3>Farm Performance</h3>
                  </div>
                </div>
                <div className="hero-card-metrics">
                  <div>
                    <p>Soil moisture</p>
                    <strong>45% steady</strong>
                  </div>
                  <div>
                    <p>Crop health</p>
                    <strong>High vigor</strong>
                  </div>
                  <div>
                    <p>Irrigation cost</p>
                    <strong>-12% vs target</strong>
                  </div>
                </div>
                <div className="hero-card-footer">
                  <span>Updated 12 min ago</span>
                  <Link to="/dashboard">Open analytics</Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="features section">
        <div className="container">
          <div className="section-header">
            <h2>Premium Capabilities</h2>
            <p>All the tools you need to run a data-driven, climate-ready farm.</p>
          </div>
          <div className="feature-grid">
            {cards.map(({ id, title, description, Icon, link }) => (
              <Link key={id} to={link} className="feature-link">
                <div className="card feature-card">
                  <span className="icon-badge">
                    <Icon size={22} />
                  </span>
                  <div>
                    <h3>{title}</h3>
                    <p>{description}</p>
                  </div>
                  <span className="feature-action">Explore →</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

export default Home;
