import React, { useCallback, useEffect, useState } from 'react';
import '../styles/IrrigationLogs.css';

const API_BASE = import.meta.env.VITE_API_BASE_URL || `http://${window.location.hostname}:8000`;

function IrrigationLogs({ cropPlanId, refreshKey }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(null);
  const [clearing, setClearing] = useState(false);

  const loadLogs = useCallback(async () => {
    if (!cropPlanId) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/irrigation/logs/${cropPlanId}?limit=20`);
      if (!response.ok) {
        throw new Error('Failed to load irrigation logs');
      }
      const data = await response.json();
      const entries = data.logs || [];
      console.log('Loaded irrigation logs:', entries.length);
      setLogs(entries);
      setLoaded(true);
    } catch (err) {
      console.error('Failed to load logs:', err);
      setError('Failed to load irrigation logs');
    } finally {
      setLoading(false);
    }
  }, [cropPlanId]);

  useEffect(() => {
    if (!cropPlanId) return;
    console.log('Loading logs - refreshKey:', refreshKey);
    loadLogs();
  }, [cropPlanId, refreshKey, loadLogs]);

  const clearLogs = async () => {
    if (!cropPlanId || !window.confirm('Are you sure you want to clear all irrigation logs?')) return;
    
    setClearing(true);
    try {
      const response = await fetch(`${API_BASE}/irrigation/logs/${cropPlanId}/clear`, {
        method: 'DELETE',
      });
      if (response.ok) {
        setLogs([]);
        console.log('Logs cleared successfully');
      } else {
        throw new Error('Failed to clear logs');
      }
    } catch (err) {
      console.error('Failed to clear logs:', err);
      setError('Failed to clear logs');
    } finally {
      setClearing(false);
    }
  };

  return (
    <div className="irrigation-logs card">
      <div className="logs-header">
        <h3>Irrigation Logs</h3>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn btn-secondary" onClick={loadLogs} disabled={loading || !cropPlanId}>
            {loaded ? 'Refresh Logs' : 'Load Logs'}
          </button>
          <button className="btn btn-danger" onClick={clearLogs} disabled={clearing || !cropPlanId || logs.length === 0}>
            {clearing ? 'Clearing...' : 'Clear Logs'}
          </button>
        </div>
      </div>

      {error && <p className="logs-error">{error}</p>}
      {loading && <p className="logs-loading">Loading logs...</p>}

      {!loading && loaded && logs.length === 0 && (
        <p className="logs-empty">No irrigation logs found for this crop plan.</p>
      )}

      {!loading && logs.length > 0 && (
        <div className="logs-table">
          <div className="logs-header-row">
            <span>Date</span>
            <span>Start Time</span>
            <span>End Time</span>
            <span>Duration</span>
            <span>Water Used</span>
            <span>Status</span>
          </div>
          {logs.map((log, index) => {
            const date = log.date || log.createdAt;
            const endTime = log.createdAt; // This is when irrigation completed
            const duration = log.durationSeconds || 0;
            
            // Calculate start time = end time - duration
            let startTime = null;
            let startTimeDisplay = 'N/A';
            let endTimeDisplay = 'N/A';
            
            if (endTime) {
              const endDate = new Date(endTime);
              // Format time without timezone conversion
              endTimeDisplay = endDate.toLocaleTimeString('en-IN', { 
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit',
                hour12: false,
                timeZone: 'Asia/Kolkata'
              });
              
              if (duration) {
                const startDate = new Date(endDate.getTime() - (duration * 1000));
                startTimeDisplay = startDate.toLocaleTimeString('en-IN', { 
                  hour: '2-digit', 
                  minute: '2-digit', 
                  second: '2-digit',
                  hour12: false,
                  timeZone: 'Asia/Kolkata'
                });
              }
            }
            
            const waterUsed = log.actualLiters || log.adjustedAmount;
            const status = log.weatherAdjustment || log.status || 'N/A';

            return (
              <div key={log.id || index} className="logs-row">
                <span>{date ? new Date(date).toLocaleDateString() : 'N/A'}</span>
                <span>{startTimeDisplay}</span>
                <span>{endTimeDisplay}</span>
                <span>{duration ? `${duration}s` : 'N/A'}</span>
                <span>{waterUsed ? `${waterUsed} L` : 'N/A'}</span>
                <span>{status}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default IrrigationLogs;
