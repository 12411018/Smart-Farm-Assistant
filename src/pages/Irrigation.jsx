import React, { useEffect, useMemo, useState } from 'react';
import { AlertTriangle, CloudDrizzle, Leaf, Wind } from 'lucide-react';
import Hero from '../components/Hero';
import IrrigationStatusCard from '../components/IrrigationStatusCard';
import IrrigationLogs from '../components/IrrigationLogs';
import { useCropContext } from '../context/CropContext';
import { getLocationWithFallback } from '../utils/locationService';
import { getWeatherData } from '../services/weatherService';
import useIrrigationLogData from '../hooks/useIrrigationLogData';
import '../styles/Irrigation.css';

const API_BASE = import.meta.env.VITE_API_BASE_URL || `http://${window.location.hostname}:8000`;

function Irrigation() {
  const { selectedPlan, selectedPlanId, selectedPlanDetails, ensurePlanDetails } = useCropContext();
  const [weather, setWeather] = useState(null);
  const [insight, setInsight] = useState(null);
  const [logsRefreshKey, setLogsRefreshKey] = useState(0);
  const { status: statusCombined, error: statusError, lastLogId, updatedAt } = useIrrigationLogData(selectedPlanId);

  useEffect(() => {
    if (selectedPlanId) {
      ensurePlanDetails(selectedPlanId);
    }
  }, [selectedPlanId, ensurePlanDetails]);

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

  const adjustmentMessage = useMemo(() => {
    if (!weather) return 'No weather adjustments detected.';
    const adjustments = [];
    if (weather.rainChance > 60) adjustments.push('Reduced due to rain forecast');
    if (weather.temperature > 35) adjustments.push('Increase due to high temperature');
    if (weather.humidity > 80) adjustments.push('Reduced due to high humidity');
    if (weather.windSpeed > 6) adjustments.push('Avoid spraying due to wind');
    return adjustments.length ? adjustments.join(' | ') : 'No weather adjustments detected.';
  }, [weather]);

  useEffect(() => {
    if (lastLogId) {
      console.log('New log ID detected, refreshing logs:', lastLogId);
      setLogsRefreshKey(Date.now()); // Use timestamp to ensure unique refresh
    }
  }, [lastLogId]);

  const formatTime = (value) => {
    if (!value) return 'N/A';
    const parsed = new Date(value);
    if (!Number.isNaN(parsed.getTime())) return parsed.toLocaleString();
    return value;
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
            recommendation={statusCombined?.start ? 'Yes' : 'No'}
            waterAmount={statusCombined?.end?.water_liters}
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

        <div className="irrigation-grid">
          <div className="card irrigation-status-panel">
            <h3>Irrigation Status</h3>
            {statusError && <p className="status-error">Status error: {statusError.message || statusError}</p>}
            {updatedAt && <p className="status-timestamp">Last updated: {new Date(updatedAt).toLocaleTimeString()}</p>}

            {statusCombined?.start || statusCombined?.end ? (
              <div className="status-grid">
                <div>
                  <span>Start Time</span>
                  <strong>{formatTime(statusCombined?.start?.start_time)}</strong>
                </div>
                <div>
                  <span>End Time</span>
                  <strong>{formatTime(statusCombined?.end?.end_time)}</strong>
                </div>
                <div>
                  <span>Duration</span>
                  <strong>{statusCombined?.end?.duration_seconds ? `${statusCombined.end.duration_seconds}s` : 'N/A'}</strong>
                </div>
                <div>
                  <span>Water Used</span>
                  <strong>{statusCombined?.end?.water_liters ? `${statusCombined.end.water_liters} L` : 'N/A'}</strong>
                </div>
                <div>
                  <span>Soil Moisture</span>
                  <strong>{statusCombined?.start?.soil ?? 'N/A'}</strong>
                </div>
                <div>
                  <span>Rain</span>
                  <strong>{statusCombined?.start?.rain ?? 'N/A'}</strong>
                </div>
              </div>
            ) : (
              <p>No irrigation start/end data available yet.</p>
            )}
          </div>

          <div className="insight-box card">
            <h3>Smart Insight</h3>
            {insight ? <p>{insight}</p> : <p>Loading crop insight...</p>}
          </div>
        </div>

        <div className="irrigation-bottom">
          <IrrigationLogs cropPlanId={selectedPlanId} refreshKey={logsRefreshKey} />
        </div>
      </div>
    </div>
  );
}

export default Irrigation;
