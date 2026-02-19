import React, { useEffect, useMemo, useState } from 'react';
import Calendar from 'react-calendar';
import { Calendar as CalendarIcon, AlertTriangle } from 'lucide-react';
import Hero from '../components/Hero';
import 'react-calendar/dist/Calendar.css';
import { useCropContext } from '../context/CropContext';
import { getLocationWithFallback } from '../utils/locationService';
import { getWeatherData } from '../services/weatherService';
import '../styles/CropCalendar.css';

const STAGE_COLORS = {
  germination: '#a7e6a1',
  vegetative: '#2f7d32',
  flowering: '#f2c94c',
  'grain-filling': '#f2994a',
  harvest: '#8d6e63',
};

function CropCalendar() {
  const {
    plans,
    selectedPlanId,
    selectPlan,
    ensurePlanDetails,
    selectedPlanDetails,
  } = useCropContext();

  const [selectedDate, setSelectedDate] = useState(new Date());
  const [weatherDaily, setWeatherDaily] = useState([]);
  const [calendarData, setCalendarData] = useState({ stages: [], irrigation: [], today: null, crop_health_score: null });

  useEffect(() => {
    if (selectedPlanId) {
      ensurePlanDetails(selectedPlanId);
    }
  }, [selectedPlanId, ensurePlanDetails]);

  useEffect(() => {
    const loadEvents = async () => {
      if (!selectedPlanId) return;
      try {
        const response = await fetch(`http://127.0.0.1:8000/calendar/${selectedPlanId}`);
        if (response.ok) {
          const data = await response.json();
          setCalendarData({
            stages: data.stages || [],
            irrigation: data.irrigation || [],
            today: data.today || null,
            crop_health_score: data.crop_health_score ?? null,
          });
        }
      } catch {
        setCalendarData({ stages: [], irrigation: [], today: null, crop_health_score: null });
      }
    };

    loadEvents();
  }, [selectedPlanId]);

  useEffect(() => {
    const loadWeather = async () => {
      try {
        const location = await getLocationWithFallback();
        const data = await getWeatherData(location.lat, location.lon);
        setWeatherDaily(data.daily || []);
      } catch {
        setWeatherDaily([]);
      }
    };

    loadWeather();
  }, []);

  const planData = selectedPlanDetails;

  const getStageForDate = (date) => {
    const dateStr = date.toISOString().split('T')[0];
    return calendarData.stages.find((stage) => {
      const start = new Date(stage.start_date).toISOString().split('T')[0];
      const end = new Date(stage.end_date).toISOString().split('T')[0];
      return dateStr >= start && dateStr <= end;
    });
  };

  const getIrrigationForDate = (date) => {
    const dateStr = date.toISOString().split('T')[0];
    return calendarData.irrigation.find((irr) => {
      const irrDate = new Date(irr.date).toISOString().split('T')[0];
      return irrDate === dateStr;
    });
  };

  const getIrrigationAmount = (irrigation) => {
    if (!irrigation) return null;
    return irrigation.water_amount ?? irrigation.water_liters ?? irrigation.waterAmountLiters ?? null;
  };

  const isIrrigationAdjusted = (irrigation) => {
    if (!irrigation) return false;
    return irrigation.adjusted ?? irrigation.auto_adjusted ?? irrigation.autoAdjusted ?? false;
  };

  const weatherAlertDates = useMemo(() => {
    if (!weatherDaily.length) return new Set();
    const alerts = new Set();
    const today = new Date();

    weatherDaily.forEach((day, index) => {
      const date = new Date(today);
      date.setDate(today.getDate() + index);
      if (day.rainChance > 60) {
        alerts.add(date.toISOString().split('T')[0]);
      }
    });

    return alerts;
  }, [weatherDaily]);

  const harvestDate = useMemo(() => {
    if (!calendarData.stages.length) return null;
    const lastStage = calendarData.stages[calendarData.stages.length - 1];
    return new Date(lastStage.end_date).toISOString().split('T')[0];
  }, [calendarData]);

  const tileClassName = ({ date, view }) => {
    if (view !== 'month') return null;
    const classes = [];
    const stage = getStageForDate(date);
    const irrigation = getIrrigationForDate(date);
    const tileDate = date.toISOString().split('T')[0];

    if (stage) {
      const stageName = stage.name.toLowerCase().replace(/\s+/g, '-');
      classes.push(`stage-${stageName}`);
    }

    if (irrigation) {
      classes.push(isIrrigationAdjusted(irrigation) ? 'irrigation-day-adjusted' : 'irrigation-day');
    }

    if (weatherAlertDates.has(tileDate)) {
      classes.push('weather-alert-day');
    }

    if (calendarData.today && tileDate === calendarData.today) {
      classes.push('today-marker');
    }

    if (harvestDate && tileDate === harvestDate) {
      classes.push('harvest-day');
    }

    return classes.join(' ');
  };

  const tileContent = ({ date, view }) => {
    if (view !== 'month') return null;
    const irrigation = getIrrigationForDate(date);
    const tileDate = date.toISOString().split('T')[0];

    return (
      <div className="tile-content">
        {irrigation && <span className="irrigation-marker"></span>}
        {weatherAlertDates.has(tileDate) && <AlertTriangle size={10} className="alert-icon" />}
      </div>
    );
  };

  const getStageColor = (stageName) => {
    if (!stageName) return STAGE_COLORS.vegetative;
    const normalized = stageName.toLowerCase().replace(/\s+/g, '-');
    return STAGE_COLORS[normalized] || STAGE_COLORS.vegetative;
  };

  if (!selectedPlanId) {
    return (
      <div className="crop-calendar-page">
        <div className="container">
          <div className="empty-state">
            <CalendarIcon size={64} />
            <h2>Select a crop from Crop Management page.</h2>
            <p>Choose a crop plan to view its lifecycle and irrigation schedule.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="crop-calendar-page">
      <div className="container">
        <Hero
          icon={<CalendarIcon size={28} />}
          title="Crop Growth Calendar"
          subtitle="Track stages, irrigation, and harvest timeline"
        />

        <div className="plan-selector">
          <label>Select Crop Plan:</label>
          <select value={selectedPlanId || ''} onChange={(e) => selectPlan(e.target.value)}>
            {plans.map((plan) => (
              <option key={plan.id} value={plan.id}>
                {plan.cropName} - {plan.location} (Planted: {new Date(plan.sowingDate).toLocaleDateString()})
              </option>
            ))}
          </select>
        </div>

        {planData && (
          <div className="calendar-grid">
            <div className="calendar-section">
              <Calendar
                onChange={setSelectedDate}
                value={selectedDate}
                tileClassName={tileClassName}
                tileContent={tileContent}
              />

              <div className="legend">
                <h3>Stage Legend</h3>
                <div className="legend-items">
                  {calendarData.stages.map((stage) => (
                    <div key={stage.name} className="legend-item">
                      <span
                        className="legend-color"
                        style={{ backgroundColor: getStageColor(stage.name) }}
                      ></span>
                      <span>{stage.name}</span>
                    </div>
                  ))}
                </div>

                <div className="legend-extra">
                  <div><span className="legend-dot"></span> Irrigation day</div>
                  <div><span className="legend-alert"></span> Weather alert</div>
                  <div><span className="legend-harvest"></span> Harvest day</div>
                </div>
              </div>
            </div>

            <div className="calendar-summary card">
              <h3>Selected Date Details</h3>
              <p><strong>Date:</strong> {selectedDate.toDateString()}</p>
              <p><strong>Stage:</strong> {getStageForDate(selectedDate)?.name || 'No stage'}</p>
              <p><strong>Irrigation:</strong> {getIrrigationAmount(getIrrigationForDate(selectedDate)) ? `${getIrrigationAmount(getIrrigationForDate(selectedDate))} L` : 'None'}</p>
              {calendarData.crop_health_score !== null && (
                <p><strong>Crop Health:</strong> {calendarData.crop_health_score}</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default CropCalendar;
