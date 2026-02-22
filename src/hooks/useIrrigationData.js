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
        console.log('ESP sensor data received:', val);
        setData(val ?? null);
        setError(null);
      },
      (err) => {
        console.error('Firebase sensor data error:', err);
        setError(err);
      }
    );

    return () => unsubscribe();
  }, []);

  return { data, error };
};

export default useIrrigationData;
