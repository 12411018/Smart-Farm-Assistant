import React, { useEffect, useMemo, useState } from 'react';
import { AlertTriangle, CloudDrizzle, Leaf, Wind, AlertCircle, CheckCircle, X } from 'lucide-react';
import Hero from '../components/Hero';
import IrrigationStatusCard from '../components/IrrigationStatusCard';
import IrrigationTable from '../components/IrrigationTable';
import IrrigationLogs from '../components/IrrigationLogs';
import { useCropContext } from '../context/CropContext';
import { getLocationWithFallback } from '../utils/locationService';
import { getWeatherData } from '../services/weatherService';
import useIrrigationData from '../hooks/useIrrigationData';
import {
  getSeason,
  locationToRegion,
  calculateCropScore,
  getBestCrop,
} from '../utils/cropRecommendationEngine';
import cropsData from '../data/cropsData.json';
import '../styles/Irrigation.css';

function Irrigation() {
  const { selectedPlan, selectedPlanId, selectedPlanDetails, ensurePlanDetails } = useCropContext();
  const { data: irrigationData } = useIrrigationData();
  const [weather, setWeather] = useState(null);
  const [insight, setInsight] = useState(null);
  const [upcomingSchedule, setUpcomingSchedule] = useState([]);
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedLocation, setSelectedLocation] = useState('');
  const [selectedSoil, setSelectedSoil] = useState('');
  const [alert, setAlert] = useState(null);
  const [recommendations, setRecommendations] = useState(null);

  useEffect(() => {
    if (selectedPlanId) {
      ensurePlanDetails(selectedPlanId);
    }
  }, [selectedPlanId, ensurePlanDetails]);

  useEffect(() => {
    const loadSchedule = async () => {
      if (!selectedPlanId) return;
      try {
        // Get soil moisture from sensor (dashboard)
        const soilMoisture = Number(irrigationData?.soilRaw ?? null);
        const url = soilMoisture ? `http://127.0.0.1:8000/irrigation/schedule/${selectedPlanId}?moisture=${soilMoisture}` : `http://127.0.0.1:8000/irrigation/schedule/${selectedPlanId}`;
        const response = await fetch(url);
        if (response.ok) {
          const data = await response.json();
          setUpcomingSchedule(data);
        }
      } catch {
        setUpcomingSchedule([]);
      }
    };

    loadSchedule();
  }, [selectedPlanId, irrigationData]);

  useEffect(() => {
    const loadWeather = async () => {
      try {
        const location = await getLocationWithFallback();
        const data = await getWeatherData(location.lat, location.lon);
        setWeather(data.current);
      } catch {
        setWeather(null);
      }
    };

    loadWeather();
  }, []);

  useEffect(() => {
    const loadInsight = async () => {
      if (!selectedPlanId || !weather) return;
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/crop-insight/${selectedPlanId}?lat=18.45&lon=73.87`
        );
        if (response.ok) {
          const data = await response.json();
          setInsight(data.insight || data);
        }
      } catch {
        setInsight(null);
      }
    };

    loadInsight();
  }, [selectedPlanId, weather]);

  const currentStage = useMemo(() => selectedPlan?.currentStage || null, [selectedPlan]);

  const todayIrrigation = useMemo(() => {
    if (!upcomingSchedule.length) return null;
    const today = new Date().toISOString().split('T')[0];
    return upcomingSchedule.find((item) => {
      const date = new Date(item.date).toISOString().split('T')[0];
      return date === today;
    });
  }, [upcomingSchedule]);

  const adjustmentMessage = useMemo(() => {
    if (!weather) return 'No weather adjustments detected.';
    const adjustments = [];
    if (weather.rainChance > 60) adjustments.push('Reduced due to rain forecast');
    if (weather.temperature > 35) adjustments.push('Increase due to high temperature');
    if (weather.humidity > 80) adjustments.push('Reduced due to high humidity');
    if (weather.windSpeed > 6) adjustments.push('Avoid spraying due to wind');
    return adjustments.length ? adjustments.join(' | ') : 'No weather adjustments detected.';
  }, [weather]);

  const nextSevenDays = useMemo(() => {
    if (!upcomingSchedule.length) return [];
    return upcomingSchedule.map((item) => {
      const dateStr = (item.date || '').split('T')[0] || item.date;
      const dateLabel = new Date(dateStr).toLocaleDateString();
      const weatherAdj = item.autoAdjusted ? 'Weather adjusted' : weather?.rainChance > 60 ? 'Rain risk' : 'Normal';
      const status = item.status || 'Pending';
      return {
        date: dateLabel,
        stage: item.stage,
        plannedWater: `${item.water || item.waterAmountLiters || ''} L`,
        weatherAdjustment: weatherAdj,
        status,
      };
    });
  }, [upcomingSchedule, weather]);

  // Auto-calculate recommendations when date, location, or soil changes
  useEffect(() => {
    if (!selectedDate || !selectedLocation || !selectedSoil) {
      setRecommendations(null);
      setAlert(null);
      return;
    }

    const calculateRecommendations = async () => {
      try {
        const season = getSeason(new Date(selectedDate));
        const region = locationToRegion(selectedLocation);

        // Coordinates and weather defaults for different locations
        const locationCoords = {
          Pune: { lat: 18.5204, lon: 73.8567, tempDefault: 28, humidityDefault: 65, rainfallDefault: 50 },
          Mumbai: { lat: 19.0760, lon: 72.8777, tempDefault: 30, humidityDefault: 75, rainfallDefault: 100 },
          Nagpur: { lat: 21.1458, lon: 79.0882, tempDefault: 27, humidityDefault: 60, rainfallDefault: 45 },
          Delhi: { lat: 28.7041, lon: 77.1025, tempDefault: 25, humidityDefault: 55, rainfallDefault: 30 },
          Kolkata: { lat: 22.5726, lon: 88.3639, tempDefault: 28, humidityDefault: 70, rainfallDefault: 80 },
          Chennai: { lat: 13.0827, lon: 80.2707, tempDefault: 32, humidityDefault: 72, rainfallDefault: 60 },
          Goa: { lat: 15.2993, lon: 73.8243, tempDefault: 32, humidityDefault: 80, rainfallDefault: 120 },
          Bangalore: { lat: 12.9716, lon: 77.5946, tempDefault: 28, humidityDefault: 68, rainfallDefault: 65 },
          Hyderabad: { lat: 17.3850, lon: 78.4867, tempDefault: 30, humidityDefault: 62, rainfallDefault: 55 },
          Jaipur: { lat: 26.9124, lon: 75.7873, tempDefault: 32, humidityDefault: 50, rainfallDefault: 35 },
          Lucknow: { lat: 26.8467, lon: 80.9462, tempDefault: 27, humidityDefault: 60, rainfallDefault: 40 },
          Indore: { lat: 22.7196, lon: 75.8577, tempDefault: 29, humidityDefault: 58, rainfallDefault: 55 },
          Bhopal: { lat: 23.1815, lon: 79.9864, tempDefault: 28, humidityDefault: 62, rainfallDefault: 50 },
          Ahmedabad: { lat: 23.0225, lon: 72.5714, tempDefault: 31, humidityDefault: 55, rainfallDefault: 45 },
        };

        const coords = locationCoords[selectedLocation] || locationCoords.Pune;

        // Fetch real weather data
        let weatherData = null;
        try {
          const apiKey = 'f3c1b26a386b403d5e0e13263d0f0511';
          const response = await fetch(
            `https://api.openweathermap.org/data/2.5/weather?lat=${coords.lat}&lon=${coords.lon}&appid=${apiKey}&units=metric`
          );
          if (response.ok) {
            const data = await response.json();
            weatherData = {
              temperature: Math.round(data.main.temp),
              humidity: data.main.humidity,
              rainfall: data.rain?.['1h'] || coords.rainfallDefault,
            };
          }
        } catch (weatherError) {
          weatherData = {
            temperature: coords.tempDefault,
            humidity: coords.humidityDefault,
            rainfall: coords.rainfallDefault,
          };
        }

        const userInputs = {
          date: selectedDate,
          location: selectedLocation,
          season,
          region,
          temperature: weatherData.temperature,
          rainfall: weatherData.rainfall,
          humidity: weatherData.humidity,
          ph: 6.5,
          soil: selectedSoil,
        };

        const scores = cropsData.map((crop) => ({
          ...crop,
          score: calculateCropScore(crop, userInputs),
        }));

        const bestCrop = getBestCrop(scores, userInputs);
        const bestCropScoreRaw = bestCrop ? calculateCropScore(bestCrop, userInputs) : 0;
        const bestCropScore = Math.round((bestCropScoreRaw / 11) * 10);

        if (bestCrop && bestCropScore > 0) {
          const topCropsScaled = scores
            .sort((a, b) => b.score - a.score)
            .slice(0, 6)
            .map(crop => ({
              ...crop,
              scoreOutOf10: Math.round((crop.score / 11) * 10)
            }));

          setRecommendations({
            season,
            region,
            topCrop: bestCrop.name,
            topScore: bestCropScore,
            temperature: userInputs.temperature,
            humidity: userInputs.humidity,
            rainfall: userInputs.rainfall,
            soil: userInputs.soil,
            allCrops: topCropsScaled,
          });

          let alertType = 'error';
          let messagePrefix = 'Not recommended';
          
          if (bestCropScore >= 7) {
            alertType = 'success';
            messagePrefix = 'Excellent choice';
          } else if (bestCropScore >= 4) {
            alertType = 'warning';
            messagePrefix = 'Can be grown';
          }

          setAlert({
            type: alertType,
            message: `${messagePrefix}: ${bestCrop.name} for ${selectedLocation} in ${season}. Compatibility: ${bestCropScore}/10`,
          });
        } else {
          setAlert({
            type: 'error',
            message: 'No suitable crops found for the selected conditions.',
          });
          setRecommendations(null);
        }
      } catch (error) {
        console.error('Recommendation error:', error);
        setAlert({ type: 'error', message: `Error: ${error.message}` });
        setRecommendations(null);
      }
    };

    calculateRecommendations();
  }, [selectedDate, selectedLocation, selectedSoil]);

  const closeAlert = () => {
    setAlert(null);
  };

  if (!selectedPlanId) {
    return (
      <div className="irrigation-page">
        <div className="container">
          <div className="irrigation-empty card">
            <AlertTriangle size={32} />
            <h2>Select a crop from Crop Management.</h2>
            <p>Choose a plan to open the irrigation control center.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="irrigation-page">
      <div className="container">
        <Hero
          icon={<Leaf size={28} />}
          title="Irrigation Control Center"
          subtitle="Real-time decisions and upcoming water plans."
        />

        <div className="irrigation-grid">
          <IrrigationStatusCard
            cropName={selectedPlan?.cropName}
            stage={currentStage}
            recommendation={todayIrrigation ? 'Yes' : 'No'}
            waterAmount={todayIrrigation?.water || todayIrrigation?.waterAmountLiters}
            method={selectedPlan?.irrigationMethod}
            adjustment={adjustmentMessage}
          />

          <div className="weather-intel card">
            <h3>Weather Intelligence</h3>
            {weather ? (
              <div className="weather-grid">
                <div><span>Temp</span><strong>{weather.temperature} C</strong></div>
                <div><span>Humidity</span><strong>{weather.humidity}%</strong></div>
                <div><span>Rain Chance</span><strong>{weather.rainChance}%</strong></div>
                <div><span>Wind</span><strong>{weather.windSpeed} m/s</strong></div>
              </div>
            ) : (
              <p>Weather data unavailable</p>
            )}
            <div className="weather-alerts">
              {weather?.rainChance > 60 && (
                <span><CloudDrizzle size={14} /> High rain risk</span>
              )}
              {weather?.windSpeed > 6 && (
                <span><Wind size={14} /> Windy conditions</span>
              )}
            </div>
          </div>
        </div>

        <div className="recommendation-section card">
          <h3>Crop Recommendation Engine</h3>
          {alert && (
            <div className={`alert alert-${alert.type}`}>
              <div className="alert-content">
                {alert.type === 'success' && <CheckCircle size={20} />}
                {alert.type === 'error' && <AlertCircle size={20} />}
                {alert.type === 'warning' && <AlertTriangle size={20} />}
                <span>{alert.message}</span>
              </div>
              <button className="alert-close" onClick={closeAlert}>
                <X size={16} />
              </button>
            </div>
          )}

          <div className="recommendation-form">
            <div className="form-group">
              <label htmlFor="date">Select Date</label>
              <input
                id="date"
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="form-control"
              />
            </div>

            <div className="form-group">
              <label htmlFor="location">Select Location</label>
              <select
                id="location"
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(e.target.value)}
                className="form-control"
              >
                <option value="">Choose a location...</option>
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
              <label htmlFor="soil">Soil Type</label>
              <select
                id="soil"
                value={selectedSoil}
                onChange={(e) => setSelectedSoil(e.target.value)}
                className="form-control"
              >
                <option value="">Choose soil type...</option>
                <option value="Loamy">Loamy (Balanced soil)</option>
                <option value="Sandy">Sandy (Quick-draining)</option>
                <option value="Clayey">Clayey (Water-retentive)</option>
                <option value="Black">Black (Fertile, cotton soil)</option>
                <option value="Red">Red (Iron-rich soil)</option>
                <option value="Alluvial">Alluvial (River deposits)</option>
                <option value="Laterite">Laterite (Well-drained tropical)</option>
              </select>
            </div>
          </div>

          {recommendations && (
            <>
              <div className="compatibility-meter">
                <h4>🏆 Best Crop: {recommendations.topCrop}</h4>
                <div className="meter-bar">
                  <div
                    className={`meter-fill ${
                      recommendations.topScore >= 8
                        ? 'green'
                        : recommendations.topScore >= 6
                        ? 'orange'
                        : 'red'
                    }`}
                    style={{
                      width: `${(recommendations.topScore / 10) * 100}%`,
                    }}
                  />
                </div>
                <span className="meter-label">
                  Compatibility: {recommendations.topScore}/10
                </span>
              </div>

              <div className="result-grid">
                <div className="result-card">
                  <strong>Season</strong>
                  <p>{recommendations.season}</p>
                </div>
                <div className="result-card">
                  <strong>Region</strong>
                  <p>{recommendations.region}</p>
                </div>
                <div className="result-card">
                  <strong>Temperature</strong>
                  <p>{recommendations.temperature}°C</p>
                </div>
                <div className="result-card">
                  <strong>Humidity</strong>
                  <p>{recommendations.humidity}%</p>
                </div>
                <div className="result-card">
                  <strong>Rainfall</strong>
                  <p>{recommendations.rainfall}mm</p>
                </div>
                <div className="result-card">
                  <strong>Soil Type</strong>
                  <p>{recommendations.soil}</p>
                </div>
              </div>

              <h4>🌾 Top Crop Options</h4>
              <div className="result-grid">
                {recommendations.allCrops.map((crop, idx) => (
                  <div key={idx} className="result-card">
                    <strong>{crop.name}</strong>
                    <p>Compatibility: {crop.scoreOutOf10}/10</p>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        <IrrigationTable rows={nextSevenDays} />

        <div className="irrigation-bottom">
          <IrrigationLogs cropPlanId={selectedPlanId} />
          <div className="insight-box card">
            <h3>Smart Insight</h3>
            {insight ? <p>{insight}</p> : <p>Loading crop insight...</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Irrigation;
