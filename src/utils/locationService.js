const DEFAULT_LOCATION = { lat: 18.5204, lon: 73.8567 }; // Pune fallback

export const getCurrentLocation = () =>
  new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject('Geolocation not supported');
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          lat: position.coords.latitude,
          lon: position.coords.longitude,
        });
      },
      (error) => {
        reject(error.message);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    );
  });

export const getLocationWithFallback = async () => {
  try {
    const location = await getCurrentLocation();
    return location;
  } catch (error) {
    console.warn('Geolocation error:', error, 'Using default location');
    return DEFAULT_LOCATION;
  }
};
