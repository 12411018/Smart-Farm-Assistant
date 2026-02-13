import React, { useCallback, useState } from 'react';
import { collection, getDocs, orderBy, query, where, limit as limitDocs } from 'firebase/firestore';
import { firestore } from '../firebase';
import '../styles/IrrigationLogs.css';

function IrrigationLogs({ cropPlanId }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(null);

  const loadLogs = useCallback(async () => {
    if (!cropPlanId) return;

    setLoading(true);
    setError(null);

    try {
      const logsQuery = query(
        collection(firestore, 'irrigation_logs'),
        where('cropPlanId', '==', cropPlanId),
        orderBy('createdAt', 'desc'),
        limitDocs(20)
      );
      const snapshot = await getDocs(logsQuery);
      const entries = snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
      setLogs(entries);
      setLoaded(true);
    } catch (err) {
      setError('Failed to load irrigation logs');
    } finally {
      setLoading(false);
    }
  }, [cropPlanId]);

  return (
    <div className="irrigation-logs card">
      <div className="logs-header">
        <h3>Irrigation Logs</h3>
        <button className="btn btn-secondary" onClick={loadLogs} disabled={loading || !cropPlanId}>
          {loaded ? 'Refresh Logs' : 'Load Logs'}
        </button>
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
            <span>Water Used</span>
            <span>Moisture Before</span>
            <span>Moisture After</span>
            <span>Auto</span>
            <span>Weather Adj</span>
          </div>
          {logs.map((log) => (
            <div key={log.id} className="logs-row">
              <span>{log.date ? new Date(log.date).toLocaleDateString() : 'N/A'}</span>
              <span>{log.adjustedAmount ? `${log.adjustedAmount} L` : 'N/A'}</span>
              <span>{log.soilMoistureBefore ?? 'N/A'}</span>
              <span>{log.soilMoistureAfter ?? 'N/A'}</span>
              <span>{log.autoTriggered ? 'Yes' : 'No'}</span>
              <span>{log.weatherAdjustment || 'None'}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default IrrigationLogs;
