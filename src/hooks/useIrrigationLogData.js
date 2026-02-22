import { useEffect, useState, useRef } from 'react';
import { onValue, ref } from 'firebase/database';
import { database } from '../firebase';

const API_BASE = import.meta.env.VITE_API_BASE_URL || `http://${window.location.hostname}:8000`;

// Listens to Firebase RTDB for real-time start/end updates (only triggers when ESP writes data)
const useIrrigationLogData = (planId) => {
  const [status, setStatus] = useState({ start: null, end: null });
  const [error, setError] = useState(null);
  const [lastLogId, setLastLogId] = useState(null);
  const [updatedAt, setUpdatedAt] = useState(null);
  const savingRef = useRef(false);
  const lastSavedSignature = useRef(null);

  useEffect(() => {
    if (!planId) return undefined;

    const normalizePayload = (val) => {
      if (!val) return null;
      if (Array.isArray(val)) {
        return val.length ? val[val.length - 1] : null;
      }
      if (typeof val === 'object') return val;
      return { value: val };
    };

    const startRef = ref(database, `irrigation/status/${planId}/start`);
    const endRef = ref(database, `irrigation/status/${planId}/end`);

    let currentStart = null;
    let currentEnd = null;

    const updateStatus = () => {
      const newStatus = { start: currentStart, end: currentEnd };
      setStatus(newStatus);
      setUpdatedAt(Date.now());
    };

    const unsubStart = onValue(
      startRef,
      (snapshot) => {
        const val = snapshot.val();
        currentStart = normalizePayload(val);
        updateStatus();
      },
      (err) => setError(err)
    );

    const unsubEnd = onValue(
      endRef,
      (snapshot) => {
        const val = snapshot.val();
        currentEnd = normalizePayload(val);
        console.log('End data from Firebase:', currentEnd);
        updateStatus();
        
        // Immediately save when end data arrives (irrigation completed)
        if (currentEnd && !savingRef.current) {
          // Create unique signature using end_time + duration + water_liters to identify unique irrigation events
          const uniqueKey = `${currentEnd.end_time || ''}_${currentEnd.duration_seconds || ''}_${currentEnd.water_liters || ''}`;
          console.log('Checking signature - Current:', uniqueKey);
          console.log('Checking signature - Last saved:', lastSavedSignature.current);
          
          if (uniqueKey !== lastSavedSignature.current) {
            console.log('ESP end data received, saving to backend:', currentEnd);
            savingRef.current = true;
            lastSavedSignature.current = uniqueKey;

            fetch(`${API_BASE}/irrigation/logs/status/${planId}`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ start: currentStart, end: currentEnd }),
            })
              .then((resp) => {
                if (!resp.ok) {
                  throw new Error(`Backend returned ${resp.status}: ${resp.statusText}`);
                }
                return resp.json();
              })
              .then((data) => {
                console.log('Backend save response:', data);
                if (data.logId) {
                  setLastLogId(data.logId);
                  console.log('New log saved with ID:', data.logId);
                }
                savingRef.current = false;
              })
              .catch((err) => {
                console.error('Failed to save irrigation status:', err);
                setError(err);
                savingRef.current = false;
              });
          }
        }
      },
      (err) => setError(err)
    );

    return () => {
      unsubStart();
      unsubEnd();
    };
  }, [planId]);

  return { status, error, lastLogId, updatedAt };
};

export default useIrrigationLogData;
