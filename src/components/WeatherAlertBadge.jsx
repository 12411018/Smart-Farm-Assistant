import React from 'react';
import { AlertTriangle, CheckCircle, CloudDrizzle } from 'lucide-react';
import '../styles/WeatherAlertBadge.css';

const iconMap = {
  low: CheckCircle,
  medium: CloudDrizzle,
  high: AlertTriangle,
};

function WeatherAlertBadge({ level = 'low', text = 'No risk' }) {
  const Icon = iconMap[level] || CheckCircle;

  return (
    <span className={`weather-alert-badge ${level}`} title={text}>
      <Icon size={14} />
      {text}
    </span>
  );
}

export default WeatherAlertBadge;
