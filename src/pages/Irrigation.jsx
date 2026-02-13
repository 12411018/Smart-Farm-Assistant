import React, { useEffect, useMemo, useState } from 'react';
import { AlertTriangle, CloudDrizzle, Leaf, Wind } from 'lucide-react';
import Hero from '../components/Hero';
import IrrigationStatusCard from '../components/IrrigationStatusCard';
import IrrigationTable from '../components/IrrigationTable';
import IrrigationLogs from '../components/IrrigationLogs';
import { useCropContext } from '../context/CropContext';
import { getLocationWithFallback } from '../utils/locationService';
import { getWeatherData } from '../services/weatherService';
import '../styles/Irrigation.css';

function Irrigation() {
  const { selectedPlan, selectedPlanId, selectedPlanDetails, ensurePlanDetails } = useCropContext();
  const [weather, setWeather] = useState(null);
  const [insight, setInsight] = useState(null);

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

  const currentStage = useMemo(() => {
    if (!selectedPlanDetails?.calendar) return null;
    const today = new Date().toISOString().split('T')[0];
    return selectedPlanDetails.calendar.find((stage) => {
      const start = new Date(stage.startDate).toISOString().split('T')[0];
      const end = new Date(stage.endDate).toISOString().split('T')[0];
      return today >= start && today <= end;
    });
  }, [selectedPlanDetails]);

  const todayIrrigation = useMemo(() => {
    if (!selectedPlanDetails?.irrigationSchedule) return null;
    const today = new Date().toISOString().split('T')[0];
    return selectedPlanDetails.irrigationSchedule.find((item) => {
      const date = new Date(item.date).toISOString().split('T')[0];
      return date === today;
    });
  }, [selectedPlanDetails]);

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
    if (!selectedPlanDetails?.irrigationSchedule) return [];
    const today = new Date();
    const end = new Date();
    end.setDate(today.getDate() + 7);

    return selectedPlanDetails.irrigationSchedule
      .filter((item) => {
        const date = new Date(item.date);
        return date >= today && date <= end;
      })
      .map((item) => {
        const dateLabel = new Date(item.date).toLocaleDateString();
        const weatherAdj = weather?.rainChance > 60 ? 'Rain risk' : 'Normal';
        const status = weather?.rainChance > 60 ? 'Skipped' : (item.status || 'Pending');
        return {
          date: dateLabel,
          stage: item.stage,
          plannedWater: `${item.waterAmountLiters} L`,
          weatherAdjustment: weatherAdj,
          status,
        };
      });
  }, [selectedPlanDetails, weather]);

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
            stage={currentStage?.stage}
            recommendation={todayIrrigation ? 'Yes' : 'No'}
            waterAmount={todayIrrigation?.waterAmountLiters}
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
