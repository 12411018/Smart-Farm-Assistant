import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import Footer from './components/Footer';
import Home from './pages/Home';
import YieldInput from './pages/YieldInput';
import CropManagement from './pages/CropManagement';
import CropCalendar from './pages/CropCalendar';
import Irrigation from './pages/Irrigation';
import Chatbot from './pages/Chatbot';
import Dashboard from './pages/Dashboard';
import WeatherForecast from './pages/WeatherForecast';
import './styles/globals.css';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Navigation />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/yield" element={<YieldInput />} />
            <Route path="/crop-management" element={<CropManagement />} />
            <Route path="/calendar" element={<CropCalendar />} />
            <Route path="/irrigation" element={<Irrigation />} />
            <Route path="/chatbot" element={<Chatbot />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/weather" element={<WeatherForecast />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
