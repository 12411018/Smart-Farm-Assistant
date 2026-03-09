/**
 * Calendar-only season fallback (used when no weather data available).
 * NOTE: Prefer getSeasonFromWeather() for location-aware results.
 */
export const getSeason = (date) => {
  const month = date.getMonth() + 1;
  if (month >= 12 || month <= 2) return "Winter";
  if (month >= 3 && month <= 5) return "Summer";
  if (month >= 6 && month <= 9) return "Monsoon";
  return "PostMonsoon";
};

/**
 * Climate zone classification per city.
 * Determines how aggressively weather signals override the calendar season.
 *
 * Zones:
 *  - "tropical"  : No true winter; monsoon-dominant. (Chennai, Goa, Kolkata)
 *  - "semi-arid" : Hot summers, mild winters, moderate monsoon. (Pune, Hyderabad, Ahmedabad)
 *  - "arid"      : Extreme summers, cold winters, low rainfall. (Jaipur, Delhi)
 *  - "humid"     : High humidity year-round; strong monsoon. (Goa, Kolkata)
 *  - "temperate" : Cooler, pronounced seasons. (Bangalore)
 */
const cityClimateZone = {
  Chennai:   "tropical",
  Goa:       "tropical",
  Kolkata:   "tropical",
  Mumbai:    "tropical",
  Hyderabad: "semi-arid",
  Pune:      "semi-arid",
  Ahmedabad: "semi-arid",
  Nagpur:    "semi-arid",
  Indore:    "semi-arid",
  Bhopal:    "semi-arid",
  Delhi:     "arid",
  Jaipur:    "arid",
  Lucknow:   "arid",
  Bangalore: "temperate",
};

/**
 * Minimum temperature threshold below which a location can be called "Winter".
 * Tropical zones never go that cold, so their threshold is much lower.
 */
const winterTempThreshold = {
  tropical:  14,  // almost never reached → effectively no "Winter"
  "semi-arid": 17,
  arid:      20,  // <20°C in Delhi/Jaipur genuinely feels like winter
  humid:     14,
  temperate: 18,
};

/**
 * getSeasonFromWeather
 * -------------------
 * Determines the agricultural season using BOTH the calendar date AND live
 * weather data fetched for the selected location's coordinates.
 *
 * Priority:
 *  1. Strong monsoon signal  → "Monsoon"
 *  2. Very high heat + dry   → "Summer"
 *  3. Cold enough for zone   → "Winter"
 *  4. Calendar default       (PostMonsoon / Winter / Summer / Monsoon)
 *
 * @param {Date}   date        - Sowing date selected by user
 * @param {Object} weatherData - { temperature, humidity, rainfall } from API
 * @param {string} city        - City string (e.g. "Chennai", "Delhi")
 * @returns {string} season    - One of: "Winter","Summer","Monsoon","PostMonsoon"
 */
export const getSeasonFromWeather = (date, weatherData, city) => {
  // If no weather data yet, fall back to calendar
  if (!weatherData) return getSeason(date);

  const { temperature, humidity, rainfall } = weatherData;
  const zone = cityClimateZone[city] || "semi-arid";
  const winterThreshold = winterTempThreshold[zone];

  // ── Strong Monsoon signal ─────────────────────────────────────────────────
  // >80mm hourly rainfall OR (high humidity AND meaningful rain AND typical months)
  const month = date.getMonth() + 1;
  const monsoonMonths = [5, 6, 7, 8, 9, 10]; // May–Oct covers regional monsoons
  const isMonthMonsoonLikely = monsoonMonths.includes(month);

  if (rainfall > 80) {
    return "Monsoon";
  }
  if (isMonthMonsoonLikely && humidity >= 78 && rainfall > 10) {
    return "Monsoon";
  }
  if (isMonthMonsoonLikely && humidity >= 85) {
    return "Monsoon"; // Even if rain API shows 0 (hourly can miss heavy days)
  }

  // ── Strong Summer signal ──────────────────────────────────────────────────
  // Very high temp + dry conditions
  if (temperature >= 36 && rainfall < 5) {
    return "Summer";
  }

  // ── Winter signal (location-adjusted) ────────────────────────────────────
  if (temperature < winterThreshold) {
    return "Winter";
  }

  // ── Mild PostMonsoon (Oct–Nov, post-rains cooling) ───────────────────────
  if ([10, 11].includes(month) && temperature < 28 && humidity > 60) {
    return "PostMonsoon";
  }

  // ── Default: use calendar month ───────────────────────────────────────────
  return getSeason(date);
};

const locationRegionMap = {
  Pune:      "Maharashtra",
  Mumbai:    "Maharashtra",
  Nagpur:    "Maharashtra",
  Indore:    "Madhya Pradesh",
  Bhopal:    "Madhya Pradesh",
  Delhi:     "North India",
  Lucknow:   "North India",
  Jaipur:    "North India",
  Kolkata:   "West Bengal",
  Chennai:   "South India",
  Bangalore: "South India",
  Hyderabad: "Telangana",
  Goa:       "Goa",
  Ahmedabad: "Gujarat",
};

export const locationToRegion = (city) => {
  return locationRegionMap[city] || "General";
};

/**
 * Returns the climate zone label for display in the UI.
 */
export const getCityClimateZone = (city) => {
  return cityClimateZone[city] || "semi-arid";
};

export const calculateCropScore = (crop, userInputs) => {
  let score = 0;

  if (crop.seasons.includes(userInputs.season)) {
    score += 3;
  }
  if (crop.soilTypes.includes(userInputs.soil)) {
    score += 2;
  }
  if (
    userInputs.temperature >= crop.tempRange[0] &&
    userInputs.temperature <= crop.tempRange[1]
  ) {
    score += 2;
  }
  if (
    userInputs.rainfall >= crop.rainfallRange[0] &&
    userInputs.rainfall <= crop.rainfallRange[1]
  ) {
    score += 2;
  }
  if (
    userInputs.humidity >= crop.humidityRange[0] &&
    userInputs.humidity <= crop.humidityRange[1]
  ) {
    score += 1;
  }
  if (userInputs.ph >= crop.phRange[0] && userInputs.ph <= crop.phRange[1]) {
    score += 1;
  }

  return score;
};

export const getBestCrop = (crops, userInputs) => {
  let bestCrop = null;
  let maxScore = 0;

  for (const crop of crops) {
    const score = calculateCropScore(crop, userInputs);
    if (score > maxScore) {
      maxScore = score;
      bestCrop = crop;
    }
  }

  return maxScore > 0 ? bestCrop : null;
};

// Default environmental conditions by region and season
const environmentalConditions = {
  Maharashtra: {
    Winter:      { temperature: 24, rainfall: 10,  humidity: 65, ph: 6.5, soil: "Loamy" },
    Summer:      { temperature: 32, rainfall: 200, humidity: 80, ph: 6.5, soil: "Loamy" },
    Monsoon:     { temperature: 29, rainfall: 180, humidity: 82, ph: 6.5, soil: "Loamy" },
    PostMonsoon: { temperature: 28, rainfall: 40,  humidity: 72, ph: 6.5, soil: "Loamy" },
  },
  "North India": {
    Winter:      { temperature: 14, rainfall: 15, humidity: 60, ph: 7.0, soil: "Loamy" },
    Summer:      { temperature: 38, rainfall: 80, humidity: 55, ph: 7.0, soil: "Loamy" },
    Monsoon:     { temperature: 30, rainfall: 200, humidity: 78, ph: 7.0, soil: "Loamy" },
    PostMonsoon: { temperature: 24, rainfall: 20,  humidity: 60, ph: 7.0, soil: "Loamy" },
  },
  "West Bengal": {
    Winter:      { temperature: 18, rainfall: 12,  humidity: 68, ph: 6.0, soil: "Loamy" },
    Summer:      { temperature: 34, rainfall: 80,  humidity: 78, ph: 6.0, soil: "Loamy" },
    Monsoon:     { temperature: 30, rainfall: 300, humidity: 88, ph: 6.0, soil: "Loamy" },
    PostMonsoon: { temperature: 26, rainfall: 50,  humidity: 74, ph: 6.0, soil: "Loamy" },
  },
  "South India": {
    Winter:      { temperature: 26, rainfall: 30,  humidity: 72, ph: 6.0, soil: "Loamy" },
    Summer:      { temperature: 34, rainfall: 40,  humidity: 70, ph: 6.0, soil: "Loamy" },
    Monsoon:     { temperature: 29, rainfall: 150, humidity: 82, ph: 6.0, soil: "Loamy" },
    PostMonsoon: { temperature: 27, rainfall: 100, humidity: 78, ph: 6.0, soil: "Loamy" },
  },
  General: {
    Winter:      { temperature: 20, rainfall: 15,  humidity: 65, ph: 6.5, soil: "Loamy" },
    Summer:      { temperature: 34, rainfall: 40,  humidity: 65, ph: 6.5, soil: "Loamy" },
    Monsoon:     { temperature: 29, rainfall: 200, humidity: 82, ph: 6.5, soil: "Loamy" },
    PostMonsoon: { temperature: 27, rainfall: 50,  humidity: 72, ph: 6.5, soil: "Loamy" },
  },
};

export const getEnvironmentalConditions = (region, season) => {
  const regionConditions = environmentalConditions[region] || environmentalConditions.General;
  return regionConditions[season] || regionConditions.Summer;
};

export const fetchWeatherData = async (lat, lon) => {
  try {
    const apiKey = process.env.REACT_APP_OPENWEATHER_API_KEY;
    const response = await fetch(
      `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${apiKey}&units=metric`
    );
    if (!response.ok) throw new Error("Weather API request failed");
    const data = await response.json();
    return {
      temperature: data.main.temp,
      humidity: data.main.humidity,
      rainfall: data.rain?.["1h"] || 0,
    };
  } catch (error) {
    console.error("Error fetching weather data:", error);
    return null;
  }
};
