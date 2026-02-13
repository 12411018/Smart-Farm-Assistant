import React from 'react';
import { Droplets, Leaf, ThermometerSun } from 'lucide-react';
import '../styles/IrrigationStatusCard.css';

function IrrigationStatusCard({
  cropName,
  stage,
  recommendation,
  waterAmount,
  method,
  adjustment,
}) {
  return (
    <div className="irrigation-status card">
      <div className="status-header">
        <div className="status-title">
          <Leaf size={20} />
          <div>
            <h3>{cropName || 'Select a crop'}</h3>
            <p>{stage || 'No stage selected'}</p>
          </div>
        </div>
        <div className={`recommendation ${recommendation === 'Yes' ? 'yes' : 'no'}`}>
          <Droplets size={16} />
          {recommendation || 'TBD'}
        </div>
      </div>

      <div className="status-body">
        <div>
          <span className="status-label">Recommended water</span>
          <span className="status-value">{waterAmount ? `${waterAmount} L` : 'TBD'}</span>
        </div>
        <div>
          <span className="status-label">Irrigation method</span>
          <span className="status-value">{method || 'TBD'}</span>
        </div>
      </div>

      <div className="status-adjustment">
        <ThermometerSun size={16} />
        <span>{adjustment || 'No weather adjustments detected.'}</span>
      </div>
    </div>
  );
}

export default IrrigationStatusCard;
