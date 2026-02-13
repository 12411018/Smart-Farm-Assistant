import React from 'react';
import {
  Activity,
  CloudSun,
  Droplets,
  LayoutDashboard,
  Thermometer,
  TrendingDown,
  TrendingUp,
  Wind,
} from 'lucide-react';
import useIrrigationData from '../hooks/useIrrigationData';
import '../styles/Dashboard.css';

function Dashboard() {
  const { data: irrigationData } = useIrrigationData();

  const temperatureValue = Number(irrigationData?.temperature ?? 27);
  const humidityValue = Number(irrigationData?.humidity ?? 68);
  const soilMoistureValue = Number(irrigationData?.soilRaw ?? 45);
  const soilPhValue = Number(irrigationData?.pH ?? 6.8);

  const farmMetrics = [
    {
      id: 1,
      title: 'Soil pH',
      Icon: Activity,
      value: soilPhValue,
      unit: 'pH level',
      status: 'optimal',
      trend: 'up',
      change: '+0.2',
      min: 6.5,
      max: 7.5,
    },
    {
      id: 2,
      title: 'Temperature',
      Icon: Thermometer,
      value: temperatureValue,
      unit: '°C',
      status: 'good',
      trend: 'up',
      change: '+1.4°',
      min: 20,
      max: 35,
    },
    {
      id: 3,
      title: 'Soil Moisture',
      Icon: Droplets,
      value: soilMoistureValue,
      unit: '%',
      status: 'good',
      trend: 'down',
      change: '-3%',
      min: 30,
      max: 60,
    },
    {
      id: 4,
      title: 'Humidity',
      Icon: Wind,
      value: humidityValue,
      unit: '%',
      status: 'optimal',
      trend: 'up',
      change: '+4%',
      min: 50,
      max: 80,
    },
  ];

  const weatherInfo = {
    condition: 'Partly Cloudy',
    Icon: CloudSun,
    temperature: '28°C',
    windSpeed: '12 km/h',
    rainfall: '0 mm',
    pressure: '1013 mb',
  };

  const cropStatus = [
    { crop: 'Wheat', stage: 'Vegetative Growth', days: '32/120', health: 'Excellent' },
    { crop: 'Rice', stage: 'Flowering', days: '85/145', health: 'Good' },
    { crop: 'Corn', stage: 'Heading', days: '58/110', health: 'Good' },
  ];

  const getStatusColor = (status) => {
    if (status === 'optimal') return '#27ae60';
    if (status === 'good') return '#2d7a4a';
    if (status === 'warning') return '#f39c12';
    if (status === 'critical') return '#e74c3c';
    return '#7f8c8d';
  };

  return (
    <div className="dashboard-page">
      <div className="container">
        <div className="dashboard-header">
          <div className="header-icon">
            <LayoutDashboard size={28} />
          </div>
          <h1>Farm Dashboard</h1>
          <p>Real-time monitoring of your farm metrics and crop status.</p>
        </div>

        <div className="dashboard-grid">
          {/* Metrics Cards */}
          <div className="metrics-section">
            <h2>Farm Metrics</h2>
            <div className="metrics-grid">
              {farmMetrics.map((metric) => (
                <div key={metric.id} className="metric-card card">
                  <div className="metric-header">
                    <span className="icon-badge">
                      <metric.Icon size={20} />
                    </span>
                    <div className={`trend ${metric.trend}`}>
                      {metric.trend === 'up' ? (
                        <TrendingUp size={14} />
                      ) : (
                        <TrendingDown size={14} />
                      )}
                      <span>{metric.change}</span>
                    </div>
                  </div>
                  <h3>{metric.title}</h3>
                  <div className="metric-value-container">
                    <span className="metric-value">{metric.value}</span>
                    <span className="metric-unit">{metric.unit}</span>
                  </div>
                  <div className="mini-chart"></div>
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{
                        width: `${((metric.value - metric.min) / (metric.max - metric.min)) * 100}%`,
                        backgroundColor: getStatusColor(metric.status),
                      }}
                    ></div>
                  </div>
                  <p className="metric-status">Status: {metric.status}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Weather Card */}
          <div className="weather-section">
            <div className="card weather-info-card">
              <h2>Current Weather</h2>
              <div className="weather-main">
                <div className="weather-icon-large">
                  <weatherInfo.Icon size={40} />
                </div>
                <div className="weather-details">
                  <p className="weather-condition">{weatherInfo.condition}</p>
                  <p className="weather-temp">{weatherInfo.temperature}</p>
                </div>
              </div>
              <div className="weather-metrics">
                <div className="weather-item">
                  <span className="weather-label">Wind Speed</span>
                  <span className="weather-value">{weatherInfo.windSpeed}</span>
                </div>
                <div className="weather-item">
                  <span className="weather-label">Rainfall</span>
                  <span className="weather-value">{weatherInfo.rainfall}</span>
                </div>
                <div className="weather-item">
                  <span className="weather-label">Pressure</span>
                  <span className="weather-value">{weatherInfo.pressure}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Crop Status Table */}
          <div className="crop-status-section">
            <div className="card crop-status-card">
              <h2>Crop Status</h2>
              <div className="crop-table">
                <div className="crop-header">
                  <div className="crop-col">Crop Name</div>
                  <div className="crop-col">Growth Stage</div>
                  <div className="crop-col">Progress</div>
                  <div className="crop-col">Health</div>
                </div>
                {cropStatus.map((crop, index) => (
                  <div key={index} className="crop-row">
                    <div className="crop-col" data-label="Crop Name">
                      {crop.crop}
                    </div>
                    <div className="crop-col" data-label="Growth Stage">
                      {crop.stage}
                    </div>
                    <div className="crop-col" data-label="Progress">
                      <div className="progress-small">
                        <div
                          className="progress-small-fill"
                          style={{
                            width: `${(parseInt(crop.days.split('/')[0]) / parseInt(crop.days.split('/')[1])) * 100}%`,
                          }}
                        ></div>
                      </div>
                      <span className="progress-text">{crop.days}</span>
                    </div>
                    <div className="crop-col" data-label="Health">
                      <span className={`health-badge health-${crop.health.toLowerCase()}`}>
                        {crop.health}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="stats-section">
            <div className="card stats-card">
              <h2>Quick Stats</h2>
              <div className="stats-items">
                <div className="stat-item">
                  <span className="stat-label">Total Area</span>
                  <span className="stat-value">45.5 hectares</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Active Crops</span>
                  <span className="stat-value">3</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Avg Yield Rate</span>
                  <span className="stat-value">82%</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Water Used</span>
                  <span className="stat-value">2,340 L/day</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
