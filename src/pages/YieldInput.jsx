import React, { useState, useEffect } from 'react';
import { Leaf, Calendar, Droplets, MapPin, DollarSign, CheckCircle } from 'lucide-react';
import Hero from '../components/Hero';
import {
  getSeasonFromWeather,
  locationToRegion,
  calculateCropScore,
  getCityClimateZone,
} from '../utils/cropRecommendationEngine';
import cropsData from '../data/cropsData.json';
import '../styles/YieldInput.css';

const CROPS = ['Wheat', 'Rice', 'Cotton', 'Sugarcane', 'Maize', 'Tomato'];
const SOIL_TYPES = ['Loamy', 'Sandy', 'Clayey', 'Black', 'Red', 'Alluvial', 'Laterite'];
const IRRIGATION_METHODS = ['Drip', 'Sprinkler', 'Flood'];
const WATER_SOURCES = ['Borewell', 'Canal', 'Rainfed', 'River', 'Pond'];

function YieldInput() {
  const [formData, setFormData] = useState({
    cropName: '',
    sowingDate: '',
    location: '',
    soilType: '',
    irrigationMethod: '',
    landSizeAcres: '',
    expectedInvestment: '',
    waterSourceType: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [planId, setPlanId] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [recommendationAlert, setRecommendationAlert] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  useEffect(() => {
    // Generate recommendation if key fields are filled
    if (formData.cropName && formData.sowingDate && formData.location && formData.soilType) {
      try {
        // NOTE: Season is now calculated AFTER weather data is fetched so it
        // reflects actual conditions at the selected location, not just the month.
        const region = locationToRegion(formData.location);
        const sowingDate = new Date(formData.sowingDate);

        // City coordinate lookup — provides real lat/lon for weather API
        const locationCoords = {
          Pune: { lat: 18.5204, lon: 73.8567, tempDefault: 28, humidityDefault: 65, rainfallDefault: 50 },
          Mumbai: { lat: 19.0760, lon: 72.8777, tempDefault: 30, humidityDefault: 75, rainfallDefault: 100 },
          Nagpur: { lat: 21.1458, lon: 79.0882, tempDefault: 27, humidityDefault: 60, rainfallDefault: 45 },
          Delhi: { lat: 28.7041, lon: 77.1025, tempDefault: 18, humidityDefault: 55, rainfallDefault: 10 },
          Kolkata: { lat: 22.5726, lon: 88.3639, tempDefault: 28, humidityDefault: 70, rainfallDefault: 80 },
          Chennai: { lat: 13.0827, lon: 80.2707, tempDefault: 29, humidityDefault: 72, rainfallDefault: 20 },
          Goa: { lat: 15.2993, lon: 73.8243, tempDefault: 32, humidityDefault: 80, rainfallDefault: 120 },
          Bangalore: { lat: 12.9716, lon: 77.5946, tempDefault: 26, humidityDefault: 68, rainfallDefault: 30 },
          Hyderabad: { lat: 17.3850, lon: 78.4867, tempDefault: 30, humidityDefault: 62, rainfallDefault: 25 },
          Jaipur: { lat: 26.9124, lon: 75.7873, tempDefault: 22, humidityDefault: 50, rainfallDefault: 8 },
          Lucknow: { lat: 26.8467, lon: 80.9462, tempDefault: 20, humidityDefault: 60, rainfallDefault: 12 },
          Indore: { lat: 22.7196, lon: 75.8577, tempDefault: 25, humidityDefault: 58, rainfallDefault: 30 },
          Bhopal: { lat: 23.1815, lon: 79.9864, tempDefault: 24, humidityDefault: 62, rainfallDefault: 25 },
          Ahmedabad: { lat: 23.0225, lon: 72.5714, tempDefault: 28, humidityDefault: 55, rainfallDefault: 15 },
        };

        // Extract city from location string (e.g., "Pune, Maharashtra" → "Pune")
        const city = formData.location.split(',')[0].trim();
        const coords = locationCoords[city] || locationCoords.Pune;
        const climateZone = getCityClimateZone(city);

        // Fetch live weather from OpenWeatherMap
        const apiKey = 'f3c1b26a386b403d5e0e13263d0f0511';
        fetch(
          `https://api.openweathermap.org/data/2.5/weather?lat=${coords.lat}&lon=${coords.lon}&appid=${apiKey}&units=metric`
        )
          .then((res) => res.ok ? res.json() : null)
          .then((data) => {
            // Build weather object — fall back to location-specific defaults if API fails
            const weatherData = data ? {
              temperature: Math.round(data.main.temp),
              humidity: data.main.humidity,
              rainfall: data.rain?.['1h'] || 0,
            } : {
              temperature: coords.tempDefault,
              humidity: coords.humidityDefault,
              rainfall: coords.rainfallDefault,
            };

            // ✅ Season derived HERE — uses real temperature + humidity + rainfall
            //    from the weather API, combined with the city's climate zone.
            const season = getSeasonFromWeather(sowingDate, weatherData, city);

            const userInputs = {
              season,
              region,
              temperature: weatherData.temperature,
              humidity: weatherData.humidity,
              rainfall: weatherData.rainfall,
              ph: 6.5,
              soil: formData.soilType,
            };

            // Find the SELECTED crop from cropsData
            const selectedCrop = cropsData.find(
              (crop) => crop.name.toLowerCase() === formData.cropName.toLowerCase()
            );

            if (selectedCrop) {
              const selectedCropScoreRaw = calculateCropScore(selectedCrop, userInputs);
              const selectedCropScore = Math.round((selectedCropScoreRaw / 11) * 10);

              // Find the BEST crop for this location, season, and real weather
              const allScores = cropsData.map((crop) => ({
                ...crop,
                score: calculateCropScore(crop, userInputs),
              }));
              const bestCrop = allScores.reduce((best, crop) =>
                crop.score > best.score ? crop : best,
                allScores[0]
              );
              const bestCropScore = Math.round((bestCrop.score / 11) * 10);

              if (selectedCropScore > 0) {
                setRecommendation({
                  season,
                  climateZone,
                  region,
                  selectedCrop: selectedCrop.name,
                  selectedCropScore,
                  bestCrop: bestCrop.name,
                  bestCropScore,
                  temperature: weatherData.temperature,
                  humidity: weatherData.humidity,
                  rainfall: weatherData.rainfall,
                });

                let messageType = 'error';
                let scoreText = 'not suitable';
                if (selectedCropScore >= 7) {
                  messageType = 'success';
                  scoreText = selectedCrop.name === bestCrop.name ? 'is the best choice' : 'is well-suited';
                } else if (selectedCropScore >= 4) {
                  messageType = 'warning';
                  scoreText = 'can be grown';
                } else {
                  messageType = 'error';
                  scoreText = 'is not recommended';
                }

                const isBestCrop = selectedCrop.name === bestCrop.name;
                const suggestionText = !isBestCrop
                  ? `💡 Better option: ${bestCrop.name} (${bestCropScore}/10)`
                  : '🏆 This is your best option!';

                setRecommendationAlert({
                  type: messageType,
                  message: `${scoreText.charAt(0).toUpperCase() + scoreText.slice(1)} for ${city} (${season}). Match: ${selectedCropScore}/10 | ${suggestionText}`,
                });
              } else {
                setRecommendationAlert({
                  type: 'error',
                  message: `${formData.cropName} is not suitable for ${city} in ${season}. Match: 0/10 | Better option: ${bestCrop.name} (${bestCropScore}/10)`,
                });
                setRecommendation(null);
              }
            } else {
              setRecommendationAlert({
                type: 'info',
                message: `ℹ️ ${formData.cropName} is available for selection`,
              });
              setRecommendation(null);
            }
          })
          .catch(() => {
            setRecommendationAlert({
              type: 'info',
              message: `ℹ️ Unable to fetch weather for ${city}. Results may be approximate.`,
            });
            setRecommendation(null);
          });
      } catch (err) {
        setRecommendationAlert(null);
        setRecommendation(null);
      }
    } else {
      setRecommendationAlert(null);
      setRecommendation(null);
    }
  }, [formData.cropName, formData.sowingDate, formData.location, formData.soilType]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await fetch('http://127.0.0.1:8000/crop-plan/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: 'demo_user',
          cropName: formData.cropName,
          location: formData.location,
          soilType: formData.soilType,
          sowingDate: formData.sowingDate,
          irrigationMethod: formData.irrigationMethod,
          landSizeAcres: parseFloat(formData.landSizeAcres),
          expectedInvestment: formData.expectedInvestment ? parseFloat(formData.expectedInvestment) : null,
          waterSourceType: formData.waterSourceType,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create crop plan');
      }

      const data = await response.json();
      setPlanId(data.cropPlanId);
      setSuccess(true);

      // Show Firebase warning if not enabled
      if (data.firebaseEnabled === false) {
        console.warn('Firebase not configured - crop plan not saved to database');
      };

      setTimeout(() => {
        setFormData({
          cropName: '',
          sowingDate: '',
          location: '',
          soilType: '',
          irrigationMethod: '',
          landSizeAcres: '',
          expectedInvestment: '',
          waterSourceType: '',
        });
        setSuccess(false);
        setPlanId(null);
      }, 5000);
    } catch (err) {
      setError(err.message || 'Failed to create crop plan');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="yield-input-page">
      <div className="container">
        <Hero
          icon={<Leaf size={28} />}
          title="Crop Planning & Yield Input"
          subtitle="Generate intelligent crop plan with automated irrigation schedule"
        />

        {success && (
          <div className="success-message">
            <CheckCircle size={32} />
            <h2>Crop Plan Created Successfully!</h2>
            <p>Plan ID: <strong>{planId}</strong></p>
            <p>Irrigation schedule and crop calendar have been generated.</p>
          </div>
        )}

        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        <div className="form-card card glass-card">
          <form onSubmit={handleSubmit}>
            <div className="form-steps">
              <div className="step-card">
                <div className="step-title">
                  <span className="step-index">Step 1</span>
                  <h3>Crop & Soil Details</h3>
                </div>
                <div className="form-grid">
                  <div className="form-group">
                    <label>
                      <Leaf size={16} />
                      Crop Name *
                    </label>
                    <select
                      name="cropName"
                      value={formData.cropName}
                      onChange={handleChange}
                      required
                      className="form-input"
                    >
                      <option value="">Select Crop</option>
                      {CROPS.map((crop) => (
                        <option key={crop} value={crop}>{crop}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>
                      <Calendar size={16} />
                      Sowing Date *
                    </label>
                    <input
                      type="date"
                      name="sowingDate"
                      value={formData.sowingDate}
                      onChange={handleChange}
                      required
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label>
                      <MapPin size={16} />
                      Location *
                    </label>
                    <select
                      name="location"
                      value={formData.location}
                      onChange={handleChange}
                      required
                      className="form-input"
                    >
                      <option value="">Select Location</option>
                      <option value="Pune">Pune</option>
                      <option value="Mumbai">Mumbai</option>
                      <option value="Nagpur">Nagpur</option>
                      <option value="Delhi">Delhi</option>
                      <option value="Kolkata">Kolkata</option>
                      <option value="Chennai">Chennai</option>
                      <option value="Goa">Goa</option>
                      <option value="Bangalore">Bangalore</option>
                      <option value="Hyderabad">Hyderabad</option>
                      <option value="Jaipur">Jaipur</option>
                      <option value="Lucknow">Lucknow</option>
                      <option value="Indore">Indore</option>
                      <option value="Bhopal">Bhopal</option>
                      <option value="Ahmedabad">Ahmedabad</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>
                      <Leaf size={16} />
                      Soil Type *
                    </label>
                    <select
                      name="soilType"
                      value={formData.soilType}
                      onChange={handleChange}
                      required
                      className="form-input"
                    >
                      <option value="">Select Soil Type</option>
                      {SOIL_TYPES.map((soil) => (
                        <option key={soil} value={soil}>{soil}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              <div className="step-card">
                <div className="step-title">
                  <span className="step-index">Step 2</span>
                  <h3>Irrigation & Land</h3>
                </div>
                <div className="form-grid">
                  <div className="form-group">
                    <label>
                      <Droplets size={16} />
                      Irrigation Method *
                    </label>
                    <select
                      name="irrigationMethod"
                      value={formData.irrigationMethod}
                      onChange={handleChange}
                      required
                      className="form-input"
                    >
                      <option value="">Select Method</option>
                      {IRRIGATION_METHODS.map((method) => (
                        <option key={method} value={method}>{method}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>
                      <Leaf size={16} />
                      Land Size (Acres) *
                    </label>
                    <input
                      type="number"
                      name="landSizeAcres"
                      value={formData.landSizeAcres}
                      onChange={handleChange}
                      placeholder="e.g., 5"
                      step="0.1"
                      min="0.1"
                      required
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label>
                      <DollarSign size={16} />
                      Expected Investment (₹)
                    </label>
                    <input
                      type="number"
                      name="expectedInvestment"
                      value={formData.expectedInvestment}
                      onChange={handleChange}
                      placeholder="Optional"
                      step="100"
                      min="0"
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label>
                      <Droplets size={16} />
                      Water Source *
                    </label>
                    <select
                      name="waterSourceType"
                      value={formData.waterSourceType}
                      onChange={handleChange}
                      required
                      className="form-input"
                    >
                      <option value="">Select Water Source</option>
                      {WATER_SOURCES.map((source) => (
                        <option key={source} value={source}>{source}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <button type="submit" className="btn btn-primary submit-btn" disabled={loading}>
              {loading ? 'Generating Crop Plan...' : 'Generate Crop Plan'}
            </button>
          </form>

          {recommendationAlert && (
            <div className="recommendation-hint">
              <div className={`alert-hint alert-hint-${recommendationAlert.type}`}>
                <span>{recommendationAlert.message}</span>
              </div>
              {recommendation && (
                <div className="recommendation-details">
                  <p><strong>Your Selection:</strong> {recommendation.selectedCrop} - Compatibility: {recommendation.selectedCropScore}/10</p>
                  <p><strong>🏆 Best for this Season:</strong> {recommendation.bestCrop} - Compatibility: {recommendation.bestCropScore}/10</p>
                  <p className="weather-data">
                    📍 {recommendation.season} ({recommendation.climateZone} climate) |
                    🌡️ {recommendation.temperature}°C |
                    💧 {recommendation.humidity}% humidity |
                    ☔ {recommendation.rainfall}mm rain
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="info-card card">
          <h3>🌾 What happens next?</h3>
          <ul>
            <li>🌱 Crop growth stages calculated automatically</li>
            <li>💧 Complete irrigation schedule generated</li>
            <li>📅 Crop calendar events created in Firebase</li>
            <li>🌦 Weather-based adjustments applied in real-time</li>
            <li>🤖 AI-powered crop insights available</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default YieldInput;
