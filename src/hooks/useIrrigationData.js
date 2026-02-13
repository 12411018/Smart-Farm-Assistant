import { useEffect, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { database } from '../firebase';

const useIrrigationData = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const dataRef = ref(database, 'irrigation');
    const unsubscribe = onValue(
      dataRef,
      (snapshot) => {
        setData(snapshot.val());
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
