const OPENWEATHER_API_KEY = "b2c7f598a005af47595d4624f4a70ff9";
const BASE_URL = "https://api.openweathermap.org/data/2.5";
const DEFAULT_LOCATION = { lat: 28.6139, lon: 77.209 }; // Delhi fallback

const buildLocationLabel = (city, country) => {
  const safeCity = city && city.trim().length > 0 ? city : 'Unknown City';
  const safeCountry = country && country.trim().length > 0 ? country : 'IN';
  return `${safeCity}, ${safeCountry}`;
};

export const getWeatherData = async (latitude = DEFAULT_LOCATION.lat, longitude = DEFAULT_LOCATION.lon) => {
  try {
    const response = await fetch(
      `${BASE_URL}/forecast?lat=${latitude}&lon=${longitude}&units=metric&appid=${OPENWEATHER_API_KEY}`
    );

    if (!response.ok) {
      throw new Error("Weather data fetch failed");
    }

    const data = await response.json();

    return {
      current: {
        temperature: Math.round(data.list[0].main.temp),
        humidity: data.list[0].main.humidity,
        windSpeed: data.list[0].wind.speed,
        rainChance: Math.round(data.list[0].pop * 100),
        rainMm: data.list[0].rain?.["3h"] || 0,
        condition: data.list[0].weather[0].main,
        description: data.list[0].weather[0].description,
      },

      hourly: data.list.slice(0, 8).map((item) => ({
        time: new Date(item.dt * 1000).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
        temperature: Math.round(item.main.temp),
        rainChance: Math.round(item.pop * 100),
        condition: item.weather[0].main,
      })),

      daily: getDailyForecast(data.list),
      city: data.city.name,
      country: data.city.country,
      locationLabel: buildLocationLabel(data.city.name, data.city.country),
    };
  } catch (error) {
    console.error("Weather API error:", error);
    throw error;
  }
};

const getDailyForecast = (forecastList) => {
  const dailyData = {};

  forecastList.forEach((item) => {
    const date = new Date(item.dt * 1000);
    const dayKey = date.toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
    });

    if (!dailyData[dayKey]) {
      dailyData[dayKey] = {
        temps: [],
        rainChances: [],
        conditions: [],
      };
    }

    dailyData[dayKey].temps.push(item.main.temp);
    dailyData[dayKey].rainChances.push(item.pop * 100);
    dailyData[dayKey].conditions.push(item.weather[0].main);
  });

  return Object.keys(dailyData)
    .slice(0, 7)
    .map((day) => ({
      day,
      minTemp: Math.round(Math.min(...dailyData[day].temps)),
      maxTemp: Math.round(Math.max(...dailyData[day].temps)),
      rainChance: Math.round(Math.max(...dailyData[day].rainChances)),
      condition: dailyData[day].conditions[0],
    }));
};

export const getWeatherInsights = (currentWeather) => {
  const insights = [];

  if (currentWeather.rainChance > 40) {
    insights.push("Rain expected soon. Avoid irrigation today.");
  }

  if (currentWeather.temperature > 32) {
    insights.push("High temperature. Monitor soil moisture closely.");
  }

  if (currentWeather.rainChance < 20 && currentWeather.temperature > 28) {
    insights.push("Dry and warm. Plan regular watering schedule.");
  }

  return insights;
};
