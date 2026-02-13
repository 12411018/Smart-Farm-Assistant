import React, { useMemo } from 'react';
import { Calendar, Droplets, MapPin, Trash2 } from 'lucide-react';
import CropProgress from './CropProgress';
import WeatherAlertBadge from './WeatherAlertBadge';
import '../styles/CropCard.css';

function CropCard({
  plan,
  details,
  onViewCalendar,
  onOpenIrrigation,
  onDelete,
  weatherRisk,
}) {
  const sowingDate = plan?.sowingDate ? new Date(plan.sowingDate) : null;
  const daysSince = useMemo(() => {
    if (!sowingDate) return 0;
    const diff = Date.now() - sowingDate.getTime();
    return Math.max(0, Math.floor(diff / (1000 * 60 * 60 * 24)));
  }, [sowingDate]);

  const totalDays = plan?.growthDurationDays || 0;

  const currentStage = useMemo(() => {
    if (!details?.calendar) return null;
    const today = new Date().toISOString().split('T')[0];
    return details.calendar.find((stage) => {
      const start = new Date(stage.startDate).toISOString().split('T')[0];
      const end = new Date(stage.endDate).toISOString().split('T')[0];
      return today >= start && today <= end;
    });
  }, [details]);

  const nextIrrigation = useMemo(() => {
    if (!details?.irrigationSchedule) return null;
    const today = new Date().toISOString();
    const upcoming = details.irrigationSchedule
      .filter((entry) => entry.date >= today)
      .sort((a, b) => new Date(a.date) - new Date(b.date));
    return upcoming[0] || null;
  }, [details]);

  return (
    <div className="crop-card">
      <div className="crop-card-header">
        <div>
          <h3>{plan.cropName}</h3>
          <p className="crop-location">
            <MapPin size={14} />
            {plan.location}
          </p>
        </div>
        <button className="crop-delete" onClick={() => onDelete(plan)} title="Delete crop plan">
          <Trash2 size={16} />
        </button>
      </div>

      <div className="crop-meta">
        <div className="crop-meta-item">
          <Calendar size={14} />
          <span>Sowing: {sowingDate ? sowingDate.toLocaleDateString() : 'N/A'}</span>
        </div>
        <div className="crop-meta-item">
          <Droplets size={14} />
          <span>Next irrigation: {nextIrrigation ? new Date(nextIrrigation.date).toLocaleDateString() : 'TBD'}</span>
        </div>
      </div>

      <div className="crop-stage">
        <span className="stage-label">Current stage</span>
        <span className="stage-value">{currentStage?.stage || 'Not started'}</span>
      </div>

      <CropProgress daysSince={daysSince} totalDays={totalDays} />

      <div className="crop-status-row">
        <div>
          <span className="status-label">Days since sowing</span>
          <span className="status-value">{daysSince} days</span>
        </div>
        <div>
          <span className="status-label">Weather risk</span>
          <WeatherAlertBadge level={weatherRisk?.level} text={weatherRisk?.text || 'No risk'} />
        </div>
      </div>

      <div className="crop-actions">
        <button className="btn btn-secondary" onClick={() => onViewCalendar(plan)}>
          View Calendar
        </button>
        <button className="btn btn-primary" onClick={() => onOpenIrrigation(plan)}>
          Open Irrigation
        </button>
      </div>
    </div>
  );
}

export default CropCard;
