import React, { useMemo } from 'react';
import '../styles/CropProgress.css';

function CropProgress({ daysSince, totalDays }) {
  const percent = useMemo(() => {
    if (!totalDays || totalDays <= 0) return 0;
    const raw = Math.round((daysSince / totalDays) * 100);
    return Math.min(100, Math.max(0, raw));
  }, [daysSince, totalDays]);

  const circleStyle = useMemo(() => ({
    background: `conic-gradient(var(--primary) ${percent}%, rgba(31, 77, 58, 0.12) ${percent}% 100%)`,
  }), [percent]);

  return (
    <div className="crop-progress">
      <div className="progress-ring" style={circleStyle}>
        <div className="progress-ring-inner">
          <span className="progress-percent">{percent}%</span>
          <span className="progress-label">Completed</span>
        </div>
      </div>
      <div className="progress-bar">
        <div className="progress-bar-fill" style={{ width: `${percent}%` }}></div>
      </div>
      <div className="progress-meta">
        <span>{daysSince} days</span>
        <span>{totalDays} total</span>
      </div>
    </div>
  );
}

export default CropProgress;
