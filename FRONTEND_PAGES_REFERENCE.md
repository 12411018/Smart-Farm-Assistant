# 📱 Frontend Pages - Complete Reference

---

## Home Page (`/`)

### Purpose
Landing page with hero section and feature navigation cards.

### Components & Features
```
┌─────────────────────────────────────────────┐
│   Smart Farming Assistant                   │
│   Crop planning, irrigation & yield insights│
│                                             │
│  ┌────┬────┬────┬────┐                     │
│  │📊  │💧  │🤖  │📈  │                     │
│  │Yield│Irr │Chat│Dash│                    │
│  └────┴────┴────┴────┘                     │
└─────────────────────────────────────────────┘

Visual Elements:
├── Background: Gradient (green theme)
├── Hero Title: "Smart Farming Assistant"
├── Tagline: "Crop planning, irrigation & yield insights"
├── Feature Cards (4 total):
│   ├── Card 1: 📊 Yield Input
│   │   └── Click → Navigate to /yield
│   ├── Card 2: 💧 Irrigation Planning
│   │   └── Click → Navigate to /irrigation
│   ├── Card 3: 🤖 Smart Chatbot
│   │   └── Click → Navigate to /chatbot
│   └── Card 4: 📈 Dashboard
│       └── Click → Navigate to /dashboard
│
└── Style: Hover animations on cards

File: src/pages/Home.jsx
CSS: src/styles/Home.css
Colors: Green gradient, earth tones
```

---

## Yield Input Page (`/yield`)

### Purpose
Record crop information and harvest yield data for analytics.

### Form Fields
```
┌─────────────────────────────────────────────┐
│   Record Your Yield 🌾                      │
│                                             │
│  Crop Type: [Dropdown ▼]                   │
│    ├─ Wheat                                │
│    ├─ Rice                                 │
│    ├─ Corn                                 │
│    ├─ Cotton                               │
│    ├─ Sugarcane                            │
│    ├─ Soya                                 │
│    ├─ Groundnut                            │
│    ├─ Sunflower                            │
│    └─ Chickpea                             │
│                                             │
│  Profit Gained: [₹ ________]               │
│                                             │
│  Growth Period: [__] days                  │
│                                             │
│  Location: [____________]                  │
│                                             │
│  [Submit] [Reset]                          │
│                                             │
│  ✓ Success! Record saved to database       │
└─────────────────────────────────────────────┘

Functionality:
├── Form validation
│   ├── All fields required
│   ├── Profit must be valid number
│   └── Growth period > 0
├── On submit:
│   ├── Save to database via POST /crop-plans
│   ├── Show success message
│   └── Reset form for next entry
└── Error handling:
    ├── Show validation errors
    └── Retry option

File: src/pages/YieldInput.jsx
CSS: src/styles/YieldInput.css
State: Form data, submission status
```

---

## Irrigation Planning Page (`/irrigation`)

### Purpose
Interactive irrigation schedule planner with crop growth stages.

### Page Layout
```
┌─────────────────────────────────────────────────────────────┐
│   Irrigation Planning 💧                                    │
│                                                             │
│   Select Crop: [Wheat ▼]                                   │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐  │
│   │      GROWTH STAGES & IRRIGATION TIMELINE             │  │
│   │                                                     │  │
│   │  Stage 1: Seedling (0-20 days)                     │  │
│   │  ○─────○ Frequency: Every 3 days, 1000L            │  │
│   │                                                     │  │
│   │  Stage 2: Vegetative (20-60 days)                  │  │
│   │          ○─────────────○ Frequency: Every 5 days  │  │
│   │                                                     │  │
│   │  Stage 3: Flowering (60-80 days)                   │  │
│   │                     ○─────●○ Frequency: Every 3d   │  │
│   │                                                     │  │
│   │  Current: Flowering Stage                          │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                             │
│   ┌──────────────────┐  ┌──────────────────┐              │
│   │   WEATHER DATA   │  │  SENSOR DATA     │              │
│   ├──────────────────┤  ├──────────────────┤              │
│   │ 🌡️ Temp: 28°C   │  │ 💧 Soil: 45%    │              │
│   │ 💨 Humidity: 65% │  │ 🌡️ Temp: 24°C  │              │
│   │ 🌧️ Rain: 0mm    │  │ 🧪 pH: 6.8      │              │
│   │ 💨 Wind: 12 km/h│  │   Optimal ✓     │              │
│   └──────────────────┘  └──────────────────┘              │
│                                                             │
│   📋 RECOMMENDATIONS                                       │
│   • Water: 1200 liters needed today                        │
│   • Method: Drip irrigation recommended                    │
│   • Frequency: Every 3 days during flowering              │
│   • Weather: No rain expected, proceed with schedule      │
└─────────────────────────────────────────────────────────────┘
```

### Data Sources & Features
```
Dynamic Elements:
├── Crop Selector
│   └── Loads stages from backend crop_data
│
├── Growth Stages Timeline
│   ├── Visual timeline for all stages
│   ├── Highlight: Current stage
│   ├── Show: Start & end dates
│   └── Display: Recommended frequency
│
├── Weather Data (Real-time)
│   ├── Fetched from: /weather API
│   ├── Updated: Every time page loads
│   ├── Displays: Temp, humidity, rain, wind
│   └── Used for: Irrigation adjustments
│
├── Sensor Data (Simulated/Real)
│   ├── Soil moisture from: IoT sensors
│   ├── Temperature from: Sensors
│   ├── pH level from: Database
│   └── Status indicator: Good/Optimal/Warning
│
└── Recommendations Card
    ├── Water amount needed
    ├── Irrigation method
    ├── Frequency details
    └── Weather considerations

File: src/pages/Irrigation.jsx
CSS: src/styles/Irrigation.css
Integration: /weather endpoint, crop data
```

---

## Chatbot Page (`/chatbot`)

### Purpose
AI-powered farming assistant for instant advice on crops, weather, irrigation, pests, etc.

### Interface Layout
```
┌─────────────────────────────────────────────────────────────┐
│ 🤖 Smart Farming Assistant                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Bot: Hello! I am your Smart Farming Assistant.           │
│   How can I help you today?          🕐 2:34 PM           │
│                    [Read Aloud 🔊]                         │
│                                                             │
│   You: What's the best irrigation method for wheat?        │
│                                  🕐 2:35 PM [Read Aloud]   │
│                                                             │
│   Bot: For wheat in seedling stage, drip irrigation is     │
│   excellent. It saves 30-40% water compared to flood...    │
│   Frequency depends on soil type. Sandy soil needs...      │
│                            🕐 2:35 PM [Read Aloud 🔊]      │
│                                                             │
│   ┌───────────────────────────────────────────────────┐   │
│   │ Or select a quick tip:                            │   │
│   │ ┌─────────┐ ┌─────────┐ ┌─────────┐             │   │
│   │ │💧 Drill  │ │🌾 Pests │ │🌧️ Rain │             │   │
│   │ │Irrigation│ │Control  │ │Harvest │             │   │
│   │ └─────────┘ └─────────┘ └─────────┘             │   │
│   │ ┌─────────┐ ┌─────────┐ ┌─────────┐             │   │
│   │ │🌱 Soil  │ │⚡ Yield │ │📅 Season│             │   │
│   │ │Prep     │ │Boost    │ │Plan     │             │   │
│   │ └─────────┘ └─────────┘ └─────────┘             │   │
│   └───────────────────────────────────────────────────┘   │
│                                                             │
│   [🎤 Enable voice] 📝 [________________] [Send ➤]        │
│     (Speech-to-text)    (Type your message)               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Features

#### Chat Interface
```
Message Types:
├── User Messages
│   ├── Alignment: Right side
│   ├── Color: Green background
│   ├── Status: Shows timestamp
│   └── With timestamp indicator
│
└── Bot Messages
    ├── Alignment: Left side
    ├── Color: Light gray
    ├── Status: Shows timestamp
    └── Markdown formatted (lists, bold, etc.)

Message Features:
├── Timestamps for all messages
├── Auto-scroll to latest message
├── Read Aloud button for each bot message
│   └── Uses Web Audio API
├── Message history preserved in state
└── Loading indicator while waiting for response
```

#### Voice Features
```
Voice Input (🎤):
├── Web Speech API (browser-based)
├── Supported browsers: Chrome, Firefox, Safari
├── Language: English (configurable)
├── Activates speech recognition
├── Converts speech to text
└── Text inserted in input field

Voice Output (🔊):
├── Web Audio API
├── Reads bot responses aloud
├── User can control playback
└── Professional voice synthesis

Fallback:
├── If speech not supported: Button disabled
├── User types normally
└── Still gets voice output from bot
```

#### Quick Tips
```
Pre-written Cards:
├── 💧 Drill Irrigation
│   └─ "How to set up drip irrigation efficiently"
├── 🌾 Pests Control
│   └─ "Natural pest control methods for your crops"
├── 🌧️ Rain & Harvest
│   └─ "What to do when rain is imminent"
├── 🌱 Soil Prep
│   └─ "Preparing soil for next season"
├── ⚡ Yield Boost
│   └─ "Methods to increase crop yield"
└── 📅 Season Plan
    └─ "Planning for different seasons"

Interaction:
├── Click a card
└── Text is auto-inserted into input field
```

#### AI Engine
```
Process:
1. User sends message
   ↓
2. Frontend sends to POST /chat
   ├── message: User's question
   └── context: Current crop/location info
   ↓
3. Backend RAG Search
   ├── Embed question vector
   ├── Search agriculture knowledge base
   ├── Retrieve top 3 relevant documents
   └── Build context
   ↓
4. LLM Request
   ├── System prompt (farming expert)
   ├── Retrieved context
   ├── Chat history
   └── User message
   ↓
5. LLM Response
   ├── Generated answer from AI
   ├── Farmer-friendly language
   └── Includes emojis & formatting
   ↓
6. Frontend Display
   ├── Show response
   ├── Enable read-aloud
   └── Store in history
```

File: src/pages/Chatbot.jsx
CSS: src/styles/Chatbot.css
API: POST /chat
Integration: Web Speech API, LLM backend
```

---

## Dashboard Page (`/dashboard`)

### Purpose
Real-time monitoring of farm metrics, crop status, and weather.

### Page Layout
```
┌─────────────────────────────────────────────────────────────┐
│ 📊 Farm Dashboard                                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   METRICS GRID (4 Cards)                                   │
│   ┌──────────────┐  ┌──────────────┐                      │
│   │ 🌡️ Temp      │  │ 💧 Soil Mst  │                      │
│   │ 28°C         │  │ 45%          │                      │
│   │ Good ✓       │  │ Good ✓       │                      │
│   │ ↑ +1.4°     │  │ ↓ -3%        │                      │
│   └──────────────┘  └──────────────┘                      │
│   ┌──────────────┐  ┌──────────────┐                      │
│   │ 🧪 pH Level  │  │ 💨 Humidity  │                      │
│   │ 6.8         │  │ 68%          │                      │
│   │ Optimal ✓   │  │ Optimal ✓    │                      │
│   │ ↑ +0.2      │  │ ↑ +4%        │                      │
│   └──────────────┘  └──────────────┘                      │
│                                                             │
│   WEATHER CARD                                             │
│   ┌─────────────────────────────────────────────────────┐ │
│   │ 🌤️ Partly Cloudy                                  │ │
│   │ Temperature: 28°C  |  Wind: 12 km/h                │ │
│   │ Rainfall: 0mm     |  Pressure: 1013 mb            │ │
│   │ 7-Day Forecast: Mostly sunny, rain expected Thu   │ │
│   └─────────────────────────────────────────────────────┘ │
│                                                             │
│   CROP STATUS TABLE                                        │
│   ┌─────────────────────────────────────────────────────┐ │
│   │ Crop     | Stage      | Status  | Days Left       │ │
│   ├─────────────────────────────────────────────────────┤ │
│   │ Wheat    | Vegetative | ✓ Good  | 25 days         │ │
│   │ Rice     | Seedling   | ⚠️ Monitor | 7 days       │ │
│   │ Corn     | Flowering  | ✓ Optimal | 15 days       │ │
│   └─────────────────────────────────────────────────────┘ │
│                                                             │
│   STATISTICS                                               │
│   Total Active Crops: 3                                    │
│   Irrigation This Week: 5 sessions                         │
│   Average Yield Last Season: 4.2 tons/acre                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Data Components

#### Metrics Cards
```
Each Card Shows:
├── Icon (Thermometer, Droplets, etc.)
├── Title (Temperature, Soil Moisture, pH, Humidity)
├── Current Value (28°C, 45%, etc.)
├── Unit (°C, %, pH level)
├── Status Badge (Optimal, Good, Warning)
├── Trend Indicator (↑ +1.4, ↓ -3%)
├── Min/Max Range (20-35°C for temp)
└── Color coding based on status

Status Levels:
├── Optimal ✓: Green
├── Good ✓: Light green
├── Warning ⚠️: Orange
└── Critical ❌: Red
```

#### Weather Card
```
Displays:
├── Current Condition (icon + name)
├── Temperature
├── Wind Speed
├── Rainfall Amount
├── Barometric Pressure
├── 7-day forecast summary
└── Source: OpenWeather API

Updates:
├── On page load
├── Every 30 minutes (auto-refresh)
└── On manual refresh
```

#### Crop Status Table
```
Columns:
├── Crop Name
├── Current Stage
├── Health Status (✓, ⚠️, ❌)
├── Days Until Next Stage
└── Quick Actions (Edit, Monitor)

Data Source:
├── crop_plans table
├── crop_stages table
├── Current date comparison
└── Status calculated in real-time
```

#### Statistics Section
```
Shows:
├── Total Active Crops
├── Irrigations This Week
├── Average Yield Last Season
├── Water Used This Month
├── Upcoming Milestones
└── Growth Stage Distribution
```

File: src/pages/Dashboard.jsx
CSS: src/styles/Dashboard.css
Hook: useIrrigationData()
Data Sources: Multiple API endpoints
```

---

## Crop Management Page (`/crop-management`)

### Purpose
View, edit, and manage all active and past crop plans.

### Features
```
┌─────────────────────────────────────────────────────────────┐
│ 🌾 Crop Management                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Filter: [All Crops ▼] [Active ▼] [Search...]             │
│                                                             │
│ ┌─ WHEAT (Active) ──────────────────────────────────────┐ │
│ │ Location: Pune  |  Size: 5 acres                     │ │
│ │ Sowing: Mar 1, 2026  |  Est. Harvest: Jun 30, 2026  │ │
│ │ Status: Currently in Flowering Stage (15/20 days)    │ │
│ │ Irrigation: 5 of 25 completed                        │ │
│ │ Expected Yield: 6.5 tons                             │ │
│ │                                                      │ │
│ │ [Edit] [Monitor] [Full Details] [Delete]             │ │
│ └────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ RICE (Active) ────────────────────────────────────────┐ │
│ │ Location: Nashik  |  Size: 3 acres                   │ │
│ │ Sowing: May 15, 2026  |  Est. Harvest: Sep 30, 2026 │ │
│ │ Status: Seedling Stage (5/20 days)                   │ │
│ │ Irrigation: 2 of 21 completed                        │ │
│ │ Expected Yield: 4.0 tons                             │ │
│ │                                                      │ │
│ │ [Edit] [Monitor] [Full Details] [Delete]             │ │
│ └────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─ WHEAT (Completed) ────────────────────────────────────┐ │
│ │ Location: Aurangabad  |  Size: 8 acres               │ │
│ │ Sowing: Oct 1, 2025  |  Harvested: Jan 30, 2026     │ │
│ │ Status: Completed ✓                                  │ │
│ │ Actual Yield: 7.2 tons (vs 6.8 expected)            │ │
│ │ Water Used: 45,000 liters                            │ │
│ │                                                      │ │
│ │ [View Report] [Archive] [Delete]                     │ │
│ └────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Actions
```
View Options:
├── Filter by status (Active, Completed, Archived)
├── Search by crop name or location
├── Sort by date, size, or yield
└── Bulk actions (select multiple)

For Each Plan:
├── [Edit] - Modify sowing date, location, etc.
├── [Monitor] - View detailed timeline
├── [Full Details] - See all stages & schedules
└── [Delete] - Remove plan

Data Displayed:
├── Location
├── Land size (acres)
├── Sowing & expected harvest dates
├── Current stage & progress
├── Irrigation completion %
├── Expected/actual yield
└── Water usage statistics
```

File: src/pages/CropManagement.jsx
CSS: src/styles/CropManagement.css
API: GET /crop-plans/{userId}
```

---

## Crop Calendar Page (`/calendar`)

### Purpose
Visual planning of crop schedules across the year.

### Features
```
Interactive Calendar:
├── React Calendar component
├── Year-long view
├── Click on dates for details
├── Visual indicators for:
│   ├── Sowing dates (🌱)
│   ├── Growth stages (📍)
│   ├── Irrigation events (💧)
│   ├── Harvest dates (✂️)
│   └── Milestones (⭐)
│
└── Crop Stages Timeline
    ├── Seedling duration
    ├── Vegetative growth
    ├── Flowering period
    ├── Grain filling
    └── Maturity

Interactions:
├── Click date → See crop details
├── Hover → Tooltip with info
├── Color coding by crop
├── Zoom in/out timeline
└── Export calendar option
```

File: src/pages/CropCalendar.jsx
CSS: src/styles/CropCalendar.css
Component: React Calendar v6.0.0
```

---

## Weather Forecast Page (`/weather`)

### Purpose
Detailed weather forecasting with agricultural insights.

### Page Layout
```
┌─────────────────────────────────────────────────────────────┐
│ 🌤️ Weather Intelligence                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Location: Pune, Maharashtra                                │
│                                                             │
│ CURRENT CONDITIONS                                          │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ 🌤️ Partly Cloudy  │  28°C  │  65% Humidity            ││
│ │ Wind: 12 km/h     │  0mm rain  │  1013 mb pressure   ││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ 24-HOUR FORECAST (Hourly)                                 │
│ ┌──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┐        │
│ │10am  12pm   2pm    4pm    6pm    8pm   10pm  12am │        │
│ ├────────────────────────────────────────────────────┤        │
│ │29°C  30°C  28°C   26°C   24°C  22°C  20°C  19°C  │        │
│ │     Rain 30% Rain 45% Rain 60% Rain 40%          │        │
│ │☀️    ☀️    🌤️    🌧️   🌧️   ⛅    ☁️    ☁️     │        │
│ └────────────────────────────────────────────────────┘        │
│                                                             │
│ 7-DAY FORECAST                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ Sat         │ Sun        │ Mon        │ Tue       │ ││
│ │ ☀️ Sunny   │ 🌤️ Clear  │ 🌧️ Rainy  │ ⛅ Cloudy │ ││
│ │ 22-32°C    │ 21-31°C    │ 18-28°C    │ 20-30°C   │ ││
│ │ Rain: 0%   │ Rain: 5%   │ Rain: 85%  │ Rain: 15% │ ││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ 💡 AI-GENERATED INSIGHTS                                  │
│ Based on forecast and your crops:                         │
│ • Wheat (Flowering): Rain expected Mon-Tue. Pause        │
│   irrigation. Risk of lodging if heavy.                  │
│ • Rice (Early vegetative): Good conditions Sat-Sun.      │
│   Irrigate today before rain arrives.                    │
│ • Overall: Monitor Mon forecast closely. May need        │
│   drainage measures if rain exceeds 60mm.                │
│                                                             │
│ 📋 RECOMMENDATIONS                                         │
│ ✓ Recommend: Immediate irrigation for rice               │
│ ⚠️ Caution: Don't plant anything new Mon-Tue            │
│ ✓ Expect: Soil moisture increase after rainfall          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Features

#### Current Weather
```
Real-time data:
├── Temperature
├── Humidity
├── Wind speed
├── Rainfall
├── Barometric pressure
└── Weather condition with icon
```

#### Hourly Forecast
```
24-hour breakdown:
├── Temperature for each hour
├── Precipitation probability
├── Wind direction
├── Cloud cover
└── Visual condition icons
```

#### 7-Day Forecast
```
Daily summary:
├── High/Low temperature
├── Precipitation chance
├── Wind speed
├── Weather condition
└── UV index
```

#### AI Insights
```
Agricultural Analysis:
├── Crop-specific recommendations
├── Pest risk assessment
├── Irrigation timing suggestions
├── Planting/harvesting windows
└── Weather-related warnings
```

File: src/pages/WeatherForecast.jsx
CSS: src/styles/Weather.css
API: GET /weather
Data: OpenWeather API + AI analysis
```

---

## Navigation Component

```
┌─────────────────────────────────────────────────────────┐
│ 🌾 Smart Farming Assistant                             │
│                                                         │
│ [Home] [Yield] [Irrigation] [Chatbot] [Dashboard]      │
│  [Crop-Mgmt] [Calendar] [Weather] [Menu]               │
│                                                         │
└─────────────────────────────────────────────────────────┘

Features:
├── Sticky positioning (stays at top)
├── Green background (agriculture theme)
├── Logo/brand name
├── Links to all 8 pages
├── Active page highlighting
├── Responsive hamburger on mobile
├── Search functionality (optional)
└── User profile dropdown (future)

File: src/components/Navigation.jsx
CSS: src/styles/Navigation.css
```

---

## Footer Component

```
┌─────────────────────────────────────────────────────────┐
│ Smart Farming Assistant                                │
│ © 2026 Agricultural Intelligence                       │
│                                                         │
│ [Contact] [Privacy] [Terms] [Help]                     │
│ Made with 💚 for Indian Farmers                         │
│                                                         │
└─────────────────────────────────────────────────────────┘

Sections:
├── Company info
├── Quick links
├── Contact info
├── Social links
└── Copyright notice

Features:
├── Consistent styling across all pages
├── Responsive layout
├── Contact form integration
└── Newsletter signup (optional)

File: src/components/Footer.jsx
CSS: src/styles/Footer.css
```

---

## Custom Hook: useIrrigationData

```javascript
Purpose: Fetch and manage irrigation sensor data

Usage:
const { data, loading, error } = useIrrigationData();

Returns:
{
  temperature: 27,      // °C
  humidity: 68,         // %
  soilRaw: 45,         // Moisture %
  pH: 6.8,             // pH level
  loading: false,
  error: null
}

Features:
├── Fetches from IoT sensors
├── Updates periodically
├── Caches data
├── Error handling
└── Loading state

File: src/hooks/useIrrigationData.js
```

---

## Styling System

### CSS Variables (globals.css)
```css
:root {
  /* Colors */
  --primary-green: #2d5016;
  --light-green: #4a7c3d;
  --dark-gray: #2c2c2c;
  --light-gray: #f5f5f5;
  --success: #22c55e;
  --warning: #ea580c;
  
  /* Spacing */
  --spacing-xs: 0.5rem;
  --spacing-sm: 1rem;
  --spacing-md: 1.5rem;
  --spacing-lg: 2rem;
  
  /* Typography */
  --font-primary: -apple-system, BlinkMacSystemFont, Segoe UI;
  --font-size-base: 16px;
  --font-weight-normal: 400;
  --font-weight-bold: 700;
}
```

### Responsive Breakpoints
```css
Mobile: < 640px
Tablet: 640px - 1024px
Desktop: > 1024px
```

---

**Document Created**: February 21, 2026
**All 8 Pages Documented**
