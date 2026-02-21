import { useEffect, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { database } from '../firebase';

const useIrrigationData = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const dataRef = ref(database, 'irrigation_logs');
    const unsubscribe = onValue(
      dataRef,
      (snapshot) => {
        const val = snapshot.val();
        if (!val) {
          setData(null);
          setError(null);
          return;
        }

        // Pick latest log: first by outer key (e.g., device/day), then by timestamp inside
        const pickLatest = (obj) => {
          const keys = Object.keys(obj || {}).filter((k) => obj[k] != null);
          if (!keys.length) return null;
          const lastKey = keys.sort().at(-1);
          return lastKey ? obj[lastKey] : null;
        };

        let latest = val;

        if (Array.isArray(val)) {
          latest = val.filter(Boolean).at(-1) ?? null;
        } else if (typeof val === 'object') {
          const outer = pickLatest(val);
          if (outer && typeof outer === 'object' && !Array.isArray(outer)) {
            latest = pickLatest(outer) ?? outer;
          } else {
            latest = outer;
          }
        }

        setData(latest ?? null);
        setError(null);
      },
      (err) => {
        setError(err);
      }
    );

    return () => unsubscribe();
  }, []);

  return { data, error };
};

export default useIrrigationData;
