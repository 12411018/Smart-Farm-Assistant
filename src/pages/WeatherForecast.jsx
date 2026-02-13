import React, { useEffect, useState } from 'react';
import { Cloud, CloudRain, Sun, Wind, Droplets, Eye, MapPin, ShieldAlert, Droplet, Leaf } from 'lucide-react';
import '../styles/Weather.css';

function WeatherForecast() {
  const [weather, setWeather] = useState(null);
  const [rules, setRules] = useState(null);
  const [aiAdvice, setAiAdvice] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [location, setLocation] = useState(null);
  const backendBaseUrl = 'http://127.0.0.1:8000';

  useEffect(() => {
    const fetchWeather = async (lat, lon) => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch(`${backendBaseUrl}/weather-analysis`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ lat, lon, include_ai: false }),
        });

        if (!response.ok) {
          throw new Error('Weather analysis failed');
        }

        const data = await response.json();
        if (!data.weather || data.error) {
          throw new Error(data.error || 'Weather data missing');
        }

        setWeather(data.weather);
        setRules(data.rules);
      } catch (err) {
        setError(err?.message || 'Unable to load weather data. Please try again.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    const fetchAiAdvice = async (lat, lon) => {
      try {
        setAiLoading(true);
        const response = await fetch(`${backendBaseUrl}/weather-analysis`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ lat, lon, include_ai: true }),
        });

        if (!response.ok) {
          throw new Error('AI advice failed');
        }

        const data = await response.json();
        if (data.error) {
          throw new Error(data.error);
        }

        const cleaned = (data.ai_advice || '').replace(/\*\*/g, '').trim();
        setAiAdvice(cleaned);
      } catch (err) {
        console.error(err);
      } finally {
        setAiLoading(false);
      }
    };

    if (!navigator.geolocation) {
      setError('Geolocation is not supported in this browser.');
      setLoading(false);
      return;
    }

    const watchId = navigator.geolocation.watchPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setLocation({ lat: latitude, lon: longitude });
        fetchWeather(latitude, longitude);
        fetchAiAdvice(latitude, longitude);
      },
      () => {
        setError('Location access denied. Please allow location and refresh.');
        setLoading(false);
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
    );

    return () => {
      navigator.geolocation.clearWatch(watchId);
    };
  }, []);

  if (loading) {
    return <div className="weather-page"><p className="loading">Loading weather data...</p></div>;
  }

  if (error) {
    return <div className="weather-page"><p className="error">{error}</p></div>;
  }

  if (!weather) {
    return <div className="weather-page"><p className="error">No weather data available</p></div>;
  }

  const irrigationClass = rules?.irrigation ? `badge-${rules.irrigation.toLowerCase()}` : '';

  return (
    <div className="weather-page">
      <div className="container">
        <div className="weather-header">
          <div className="header-icon">
            <Cloud size={28} />
          </div>
          <h1>Weather Forecast</h1>
          <p className="location">
            <MapPin size={14} />
            {weather.location_label || (location ? `${location.lat.toFixed(2)}, ${location.lon.toFixed(2)}` : 'Live Location')}
            <span className="default-badge">Live Location</span>
          </p>
        </div>

        {/* Current Weather */}
        <div className="weather-section">
          <h2>Today's Weather</h2>
          <div className="current-weather card">
            <div className="current-main">
              <div className="weather-icon-large">
                {weather.current.condition === 'Clear' ? (
                  <Sun size={60} />
                ) : weather.current.condition === 'Rainy' || weather.current.condition === 'Rain' ? (
                  <CloudRain size={60} />
                ) : (
                  <Cloud size={60} />
                )}
              </div>
              <div className="current-info">
                <p className="condition">{weather.current.condition}</p>
                <p className="temp">{Math.round(weather.current.temp)}°C</p>
              </div>
            </div>

            <div className="current-metrics">
              <div className="metric-item">
                <Droplets size={18} />
                <span className="label">Humidity</span>
                <span className="value">{weather.current.humidity}%</span>
              </div>
              <div className="metric-item">
                <Wind size={18} />
                <span className="label">Wind Speed</span>
                <span className="value">{Math.round(weather.current.wind)} m/s</span>
              </div>
              <div className="metric-item">
                <CloudRain size={18} />
                <span className="label">Rain Chance</span>
                <span className="value">{Math.round(weather.current.rain_chance)}%</span>
              </div>
              <div className="metric-item">
                <Eye size={18} />
                <span className="label">Rain Amount</span>
                <span className="value">{Number(weather.current.rain || 0).toFixed(1)} mm</span>
              </div>
            </div>
          </div>
        </div>

        {rules && (
          <div className="weather-section">
            <h2>Irrigation Decision</h2>
            <div className="irrigation-card">
              <div className={`irrigation-badge ${irrigationClass}`}>
                <Droplet size={16} />
                <span>{rules.irrigation}</span>
              </div>
              <p className="irrigation-reason">{rules.irrigation_reason}</p>
              <div className="rule-grid">
                <div className="rule-card">
                  <ShieldAlert size={18} />
                  <div>
                    <p className="rule-title">Pest Risk</p>
                    <p className="rule-value">{rules.pest_risk}</p>
                  </div>
                </div>
                <div className="rule-card">
                  <ShieldAlert size={18} />
                  <div>
                    <p className="rule-title">Disease Risk</p>
                    <p className="rule-value">{rules.disease_risk}</p>
                  </div>
                </div>
                <div className="rule-card">
                  <Wind size={18} />
                  <div>
                    <p className="rule-title">Spray</p>
                    <p className="rule-value">{rules.spray_warning}</p>
                  </div>
                </div>
                <div className="rule-card">
                  <Leaf size={18} />
                  <div>
                    <p className="rule-title">Fertilizer</p>
                    <p className="rule-value">{rules.fertilizer_warning}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Hourly Forecast */}
        <div className="weather-section">
          <h2>Next 24 Hours</h2>
          <div className="hourly-forecast">
            {weather.hourly.map((hour, index) => (
              <div key={index} className="hourly-card">
                <p className="hour-time">{hour.time}</p>
                <div className="hour-condition">
                  {hour.condition === 'Clear' ? (
                    <Sun size={24} />
                  ) : hour.condition === 'Rainy' || hour.condition === 'Rain' ? (
                    <CloudRain size={24} />
                  ) : (
                    <Cloud size={24} />
                  )}
                </div>
                <p className="hour-temp">{hour.temp}°C</p>
                <p className="hour-rain">{hour.rain_chance}% rain</p>
              </div>
            ))}
          </div>
        </div>

        {/* Weekly Forecast */}
        <div className="weather-section">
          <h2>7-Day Forecast</h2>
          <div className="weekly-forecast">
            {weather.daily.map((day, index) => (
              <div key={index} className="daily-card">
                <p className="day-name">{day.day}</p>
                <div className="day-condition-icon">
                  {day.condition === 'Clear' ? (
                    <Sun size={32} />
                  ) : day.condition === 'Rainy' || day.condition === 'Rain' ? (
                    <CloudRain size={32} />
                  ) : (
                    <Cloud size={32} />
                  )}
                </div>
                <div className="day-temps">
                  <span className="max">{day.max}°</span>
                  <span className="min">{day.min}°</span>
                </div>
                <p className="day-rain">{day.rain_chance}% rain</p>
                <p className="day-condition">{day.condition}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="weather-section">
          <h2>AI Weather Insights</h2>
          <div className="weather-ai-card">
            {aiLoading && <p className="ai-loading">Generating AI advice...</p>}
            {!aiLoading && aiAdvice && <p className="ai-content">{aiAdvice}</p>}
            {!aiLoading && !aiAdvice && (
              <p className="ai-empty">AI advice unavailable. Please try again.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default WeatherForecast;
