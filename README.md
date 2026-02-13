git status
# 🌾 Smart Farming Assistant - Web App

A modern, responsive agriculture smart farming web application built with React. This farmer-friendly platform helps optimize crop planning, irrigation management, and yield insights with an intuitive user interface.

## ✨ Features

- **🏠 Home Page**: Beautiful hero section with quick navigation to all features
- **📊 Yield Input**: Record crop information and harvest yield data
- **💧 Irrigation Planning**: Optimize irrigation schedules based on crop growth stages and weather
- **🤖 Smart Chatbot**: AI-powered farming assistant for instant advice
- **📈 Dashboard**: Real-time monitoring of farm metrics and crop status
- **📱 Fully Responsive**: Works seamlessly on mobile, tablet, and desktop

## 🎨 Design

- **Color Scheme**: Green & earth-tone colors for agriculture theme
- **Typography**: Clean, modern fonts optimized for readability
- **Components**: Rounded cards with soft shadows and minimal animations
- **Responsive**: Mobile-first design approach

## 🛠️ Technology Stack

- **Frontend Framework**: React (Functional Components)
- **Routing**: React Router v6
- **Styling**: Plain CSS (no frameworks)
- **Build Tool**: Vite
- **Package Manager**: npm

## 📁 Project Structure

```
src/
├── components/              # Reusable components
│   ├── Navigation.jsx      # Top navigation bar
│   └── Footer.jsx          # Footer component
├── pages/                  # Page components
│   ├── Home.jsx           # Home page with hero & cards
│   ├── YieldInput.jsx     # Yield data form
│   ├── Irrigation.jsx     # Irrigation planning
│   ├── Chatbot.jsx        # Chat interface
│   └── Dashboard.jsx      # Farm metrics dashboard
├── styles/                # CSS files
│   ├── globals.css        # Global styles & variables
│   ├── Navigation.css     # Navigation styles
│   ├── Footer.css         # Footer styles
│   ├── Home.css          # Home page styles
│   ├── YieldInput.css    # Yield input styles
│   ├── Irrigation.css    # Irrigation styles
│   ├── Chatbot.css       # Chatbot styles
│   └── Dashboard.css     # Dashboard styles
├── App.jsx               # Main app component with routes
├── App.css              # App container styles
├── main.jsx             # Entry point
└── index.css            # Base styles
```

## 🚀 Getting Started

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn

### Installation

1. Navigate to the project directory:
```bash
cd c:\ENGINEERING\HACKATHON\MY_AGRI
```

2. Install dependencies:
```bash
npm install
```

### Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173/`

### Build for Production

```bash
npm run build
```

This creates an optimized production build in the `dist/` folder.

### Preview Production Build

```bash
npm run preview
```

## 📄 Pages Overview

### 1. Home Page (`/`)
- Hero section with eye-catching background
- Title: "Smart Farming Assistant"
- Subtitle highlighting key features
- 4 interactive cards for navigation:
  - Yield Input
  - Irrigation Planning
  - Chatbot
  - Dashboard

### 2. Yield Input (`/yield`)
- Form to record crop information:
  - Crop type (dropdown)
  - Profit gained (number input)
  - Crop growth period (days)
  - Location (text input)
- Success feedback on submission

### 3. Irrigation Planning (`/irrigation`)
- Crop selection dropdown
- Crop growth stages timeline
- Weather data display (placeholder)
- Soil sensor readings
- Irrigation recommendations

### 4. Chatbot (`/chatbot`)
- Chat interface with user & bot messages
- Message timestamps
- Microphone icon (UI only)
- Speaker icon for voice output (UI only)
- Quick tips section

### 5. Dashboard (`/dashboard`)
- Farm metrics cards:
  - Soil pH
  - Temperature
  - Soil Moisture
  - Humidity
- Weather information card
- Crop status table
- Quick statistics

## 🎨 Color Palette

| Color | Hex Code | Usage |
|-------|----------|-------|
| Primary Green | #2d7a4a | Headers, buttons |
| Light Green | #4a9d6f | Accents, hovers |
| Light Background | #f4f9f6 | Page backgrounds |
| White | #ffffff | Cards, text backgrounds |
| Dark Text | #2c3e50 | Body text |
| Light Text | #7f8c8d | Secondary text |
| Accent Green | #27ae60 | Highlights, success |
| Earth Brown | #8b7355 | Alternative accent |

## 🔧 Customization

### Changing Colors
Edit the CSS variables in `src/styles/globals.css`:

```css
:root {
  --primary-green: #2d7a4a;
  --light-green: #4a9d6f;
  /* ... other colors ... */
}
```

### Adding New Pages
1. Create a new component in `src/pages/`
2. Create corresponding styles in `src/styles/`
3. Import in `App.jsx` and add a route:

```jsx
<Route path="/new-page" element={<NewPage />} />
```

4. Update Navigation.jsx to include the new link

## 📱 Responsive Breakpoints

- **Desktop**: 1200px and above
- **Tablet**: 768px - 1199px
- **Mobile**: Below 768px
- **Small Mobile**: Below 480px

## ⚠️ Important Notes

- **No Backend**: This is a frontend-only application (UI/UX layer)
- **No Authentication**: No login or user management implemented
- **Placeholder Data**: All data displayed is static/placeholder
- **No API Integration**: Weather and sensor data are mocked
- **No Database**: No data persistence

## 📊 API Placeholders

The app includes placeholder sections for future integration:
- Weather API data
- Soil sensor readings
- Chatbot backend integration
- Farm database

## 🌐 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 📝 License

This project is created for educational and demonstration purposes.

## 🤝 Contributing

This is a demo project. For modifications or improvements, please follow React best practices and maintain the clean folder structure.

## 📞 Support

For questions or issues, refer to the React and Vite documentation:
- [React Documentation](https://react.dev)
- [React Router Documentation](https://reactrouter.com)
- [Vite Documentation](https://vitejs.dev)

---

**Built with ❤️ for farmers and agriculture enthusiasts**


