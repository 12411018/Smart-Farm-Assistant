import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Leaf, RefreshCw } from 'lucide-react';
import CropCard from '../components/CropCard';
import { useCropContext } from '../context/CropContext';
import { getLocationWithFallback } from '../utils/locationService';
import { getWeatherData } from '../services/weatherService';

const API_BASE = import.meta.env.VITE_API_BASE_URL || `http://${window.location.hostname}:8000`;
import '../styles/CropManagement.css';

function CropManagement() {
  const navigate = useNavigate();
  const {
    plans,
    planDetails,
    loadingPlans,
    refreshPlans,
    ensurePlanDetails,
    selectPlan,
    removePlan,
    setPlans,
  } = useCropContext();

  const [weather, setWeather] = useState(null);
  const [weatherError, setWeatherError] = useState(null);

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        const response = await fetch(
          `${API_BASE}/crop-plan/user/demo_user`
        );
        const data = await response.json();
        setPlans(data.plans);
      } catch (error) {
        console.error('Error fetching plans:', error);
      }
    };

    fetchPlans();
  }, [setPlans]);

  useEffect(() => {
    plans.forEach((plan) => ensurePlanDetails(plan.id));
  }, [plans, ensurePlanDetails]);

  useEffect(() => {
    const loadWeather = async () => {
      try {
        const location = await getLocationWithFallback();
        const data = await getWeatherData(location.lat, location.lon);
        setWeather(data.current);
      } catch (err) {
        setWeatherError('Weather data unavailable');
      }
    };

    loadWeather();
  }, []);

  const weatherRisk = useMemo(() => {
    if (!weather) return { level: 'low', text: 'No risk' };

    const riskTriggers = [];
    if (weather.rainChance > 60) riskTriggers.push('Rain');
    if (weather.temperature > 35) riskTriggers.push('Heat');
    if (weather.humidity > 80) riskTriggers.push('High humidity');
    if (weather.windSpeed > 6) riskTriggers.push('Wind');

    if (riskTriggers.length >= 3) {
      return { level: 'high', text: `${riskTriggers[0]} risk` };
    }
    if (riskTriggers.length >= 1) {
      return { level: 'medium', text: `${riskTriggers[0]} risk` };
    }
    return { level: 'low', text: 'No risk' };
  }, [weather]);

  const handleViewCalendar = (plan) => {
    selectPlan(plan.id);
    navigate('/calendar');
  };

  const handleOpenIrrigation = (plan) => {
    selectPlan(plan.id);
    navigate('/irrigation');
  };

  const handleDelete = async (plan) => {
    const confirmed = window.confirm(`Delete crop plan for ${plan.cropName}?`);
    if (!confirmed) return;

    const response = await fetch(`${API_BASE}/crop-plan/${plan.id}`, { method: 'DELETE' });
    if (response.ok) {
      removePlan(plan.id);
    }
  };

  return (
    <div className="crop-management-page">
      <div className="container">
        <div className="page-header">
          <div className="header-icon">
            <Leaf size={30} />
          </div>
          <div>
            <h1>Crop Management</h1>
            <p>Monitor each crop plan and jump to calendar or irrigation instantly.</p>
          </div>
          <button className="btn btn-secondary" onClick={refreshPlans} disabled={loadingPlans}>
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>

        {weatherError && <p className="weather-error">{weatherError}</p>}

        {plans.length === 0 && !loadingPlans && (
          <div className="empty-state card">
            <h3>No crop plans found</h3>
            <p>Create a crop plan from Yield Input to get started.</p>
          </div>
        )}

        <div className="crop-grid">
          {plans.map((plan) => (
            <CropCard
              key={plan.id}
              plan={plan}
              details={planDetails[plan.id]}
              onViewCalendar={handleViewCalendar}
              onOpenIrrigation={handleOpenIrrigation}
              onDelete={handleDelete}
              weatherRisk={weatherRisk}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

export default CropManagement;
