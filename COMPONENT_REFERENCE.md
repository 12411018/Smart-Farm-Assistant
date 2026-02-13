# Component Reference Guide

## Navigation Component
**File**: `src/components/Navigation.jsx`

### Props
None (uses React Router)

### Exports
```jsx
function Navigation() { ... }
```

### Features
- Sticky positioned navbar
- Links to all 5 pages
- Responsive menu layout
- Logo with emoji

### Usage
Already integrated in App.jsx routes

### Styling
- Primary green background
- White text with hover effects
- Responsive stacking on mobile

---

## Footer Component
**File**: `src/components/Footer.jsx`

### Props
None

### Exports
```jsx
function Footer() { ... }
```

### Features
- Fixed at bottom of page (flexbox)
- Project name and tagline
- Consistent with Navigation styling

### Usage
Already integrated in App.jsx

### Styling
- Matches Navigation colors
- Light footer with dark background
- Full width responsive

---

## Home Page
**File**: `src/pages/Home.jsx`

### Props
None (Route component)

### Exports
```jsx
function Home() { ... }
```

### State
None

### Features
```jsx
const cards = [
  { id, title, description, icon, link }
  // 4 cards for main features
]
```

### Sections
1. **Hero Section**
   - Title: "Smart Farming Assistant"
   - Subtitle: "Crop planning, irrigation & yield insights"
   - Description paragraph
   - Gradient background

2. **Feature Cards**
   - 4 clickable cards
   - Icons: 📊 💧 🤖 📈
   - Navigation links
   - Hover animations

### Styling
- Large hero with gradient background
- Grid layout for cards
- Responsive grid columns

---

## Yield Input Page
**File**: `src/pages/YieldInput.jsx`

### Props
None

### Exports
```jsx
function YieldInput() { ... }
```

### State
```jsx
const [formData, setFormData] = useState({
  crop: '',           // string
  profit: '',         // number as string
  growthPeriod: '',   // number as string
  location: ''        // string
});

const [submitted, setSubmitted] = useState(false);  // boolean
```

### Available Crops
```jsx
const crops = [
  'Select a crop',
  'Wheat', 'Rice', 'Corn', 'Sugarcane', 'Cotton',
  'Soybean', 'Millet', 'Barley'
];
```

### Methods
```jsx
handleChange(e)     // Updates form state
handleSubmit(e)     // Validates & submits form
```

### Features
- 4 form fields with validation
- Success message on submit
- Auto-reset form after submission
- Responsive form layout

### Styling
- Centered card layout
- Form input styling
- Success animation
- Mobile optimized

---

## Irrigation Planning Page
**File**: `src/pages/Irrigation.jsx`

### Props
None

### Exports
```jsx
function Irrigation() { ... }
```

### State
```jsx
const [cropName, setCropName] = useState('');           // string
const [irrigationPlan, setIrrigationPlan] = useState(null);
```

### Data Objects

**Crop Stages** (Hard-coded database):
```jsx
const cropStages = {
  Wheat: [
    { stage: string, duration: string },
    // 5 growth stages
  ],
  Rice: [...],      // 5 stages
  Corn: [...],      // 5 stages
  Cotton: [...]     // 5 stages
}
```

**Weather Data**:
```jsx
const weatherData = {
  temperature: string,
  humidity: string,
  rainfall: string,
  windSpeed: string
}
```

**Sensor Data**:
```jsx
const sensorData = {
  soilMoisture: string,
  temperature: string,
  pH: string
}
```

### Methods
```jsx
handleGeneratePlan()  // Creates plan based on crop selection
```

### Sections
1. **Crop Selection Form**
2. **Growth Stages Timeline** (conditional)
3. **Weather Data Display** (conditional)
4. **Soil Sensor Data** (conditional)
5. **Irrigation Recommendation** (conditional)

### Styling
- Grid layout for data cards
- Timeline visualization for stages
- Data grid for metrics
- Color-coded status

---

## Chatbot Page
**File**: `src/pages/Chatbot.jsx`

### Props
None

### Exports
```jsx
function Chatbot() { ... }
```

### State
```jsx
const [messages, setMessages] = useState([
  { id, text, sender: 'bot'|'user', timestamp }
]);

const [inputValue, setInputValue] = useState('');

const messagesEndRef = useRef(null);
```

### Message Object Structure
```jsx
{
  id: number,                    // unique identifier
  text: string,                  // message content
  sender: 'user'|'bot',         // message origin
  timestamp: new Date()          // creation time
}
```

### Bot Responses
```jsx
const botResponses = [
  // 8 pre-defined farming advice responses
]
```

### Methods
```jsx
handleSendMessage(e)  // Sends user message & generates bot response
scrollToBottom()      // Auto-scroll to latest message
```

### Features
- Message display with user/bot distinction
- Auto-scrolling to new messages
- Timestamps for each message
- Microphone button (UI only)
- Speaker button (UI only)
- Quick tips cards
- Chat input with send button

### Styling
- Chat bubble styling
- Message animations
- Scrollable container
- Quick tips grid

---

## Dashboard Page
**File**: `src/pages/Dashboard.jsx`

### Props
None

### Exports
```jsx
function Dashboard() { ... }
```

### State
None (all hard-coded display data)

### Data Objects

**Farm Metrics**:
```jsx
const farmMetrics = [
  {
    id: number,
    title: string,
    icon: emoji,
    value: number as string,
    unit: string,
    status: 'optimal'|'good'|'warning'|'critical',
    min: number,        // for progress bar calculation
    max: number
  }
  // 4 metrics total
]
```

**Weather Info**:
```jsx
const weatherInfo = {
  condition: string,
  icon: emoji,
  temperature: string,
  windSpeed: string,
  rainfall: string,
  pressure: string
}
```

**Crop Status**:
```jsx
const cropStatus = [
  {
    crop: string,
    stage: string,
    days: string,        // "current/total" format
    health: 'Excellent'|'Good'|'Warning'
  }
  // Multiple crops
]
```

### Methods
```jsx
getStatusColor(status)  // Returns hex color for status badge
```

### Sections
1. **Metrics Cards** (4 cards with progress bars)
2. **Weather Card** (gradient background)
3. **Crop Status Table** (rows for each crop)
4. **Quick Stats** (4 stat items)

### Styling
- Grid layout for responsive design
- Color-coded status indicators
- Progress bars
- Table layout for crop status
- Badge styling

---

## CSS Files Reference

### globals.css
- CSS custom properties (variables)
- Typography styles
- Button utilities (.btn, .btn-primary)
- Card component styles
- Base responsive utilities

### Navigation.css
- Navigation bar styling
- Logo styling
- Link hover effects
- Mobile responsive layout

### Footer.css
- Footer background and text
- Layout positioning
- Responsive adjustments

### Home.css
- Hero section background
- Feature cards grid
- Card hover animations
- Responsive grid breakpoints

### YieldInput.css
- Form container styling
- Input field styling
- Success message animations
- Form responsiveness

### Irrigation.css
- Timeline visualization
- Data grid layouts
- Card styling
- Progress bars and indicators

### Chatbot.css
- Chat bubble styling
- Message animations
- Input form layout
- Quick tips grid
- Scrollbar styling

### Dashboard.css
- Metric card styling
- Weather card gradient
- Crop status table
- Progress bar styling
- Status badges
- Responsive table layout

---

## Hooks Usage

### useState Hook
```jsx
const [state, setState] = useState(initialValue);

// Examples in app:
const [formData, setFormData] = useState({...});
const [messages, setMessages] = useState([...]);
const [cropName, setCropName] = useState('');
```

### useRef Hook
```jsx
const ref = useRef(null);

// Example in chatbot:
const messagesEndRef = useRef(null);  // For auto-scroll
```

### useEffect Hook
```jsx
useEffect(() => {
  // Side effect code
}, [dependencies]);

// Example in chatbot:
useEffect(() => {
  scrollToBottom();
}, [messages]);
```

---

## Color Variables

```css
--primary-green: #2d7a4a       /* Main action color */
--light-green: #4a9d6f         /* Hover states */
--light-bg: #f4f9f6            /* Background color */
--white: #ffffff               /* Card backgrounds */
--dark-text: #2c3e50           /* Body text */
--light-text: #7f8c8d          /* Secondary text */
--accent-green: #27ae60        /* Success/highlights */
--earth-brown: #8b7355         /* Alternative accent */
--border-color: #dae5e0        /* Borders & dividers */
--shadow: 0 2px 12px rgba(...) /* Box shadows */
```

---

## Responsive Breakpoints

```css
/* Desktop: 1200px+ */
/* Tablet: 768px - 1199px */
/* Mobile: Below 768px */
/* Small Mobile: Below 480px */
```

---

## Event Handlers Pattern

### Form Submit
```jsx
const handleSubmit = (e) => {
  e.preventDefault();  // Prevent page reload
  // Validation & processing
  setState(newValue);
};
```

### Form Input Change
```jsx
const handleChange = (e) => {
  const { name, value } = e.target;
  setState(prev => ({
    ...prev,
    [name]: value
  }));
};
```

### Click Handler
```jsx
const handleClick = () => {
  setState(newValue);
};
```

---

## Navigation Patterns

### Using React Router Link
```jsx
<Link to="/path" className="nav-link">
  Label
</Link>
```

### Using navigate Hook (not currently used)
```jsx
const navigate = useNavigate();
navigate('/path');
```

---

## Tips for Extending Components

1. **Add New Crops to Irrigation**
   - Add to `cropStages` object in Irrigation.jsx
   - Include 4-5 growth stages with durations

2. **Add New Dashboard Metrics**
   - Add to `farmMetrics` array in Dashboard.jsx
   - Set appropriate min/max for progress calculation

3. **Add New Chatbot Responses**
   - Add to `botResponses` array in Chatbot.jsx
   - Keep responses farming-related

4. **Add New Yield Input Fields**
   - Add to `formData` state
   - Create form-group div
   - Update validation logic

---

**Last Updated**: February 2026
**Version**: 1.0 Complete
