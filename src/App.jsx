import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import Footer from './components/Footer';
import AuthModal from './components/AuthModal';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';
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
    <AuthProvider>
      <Router>
        <div className="app-container">
          <Navigation />
          <main className="app-main">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/weather" element={<WeatherForecast />} />
              <Route path="/chatbot" element={<Chatbot />} />
              
              {/* Protected Routes */}
              <Route
                path="/yield"
                element={
                  <ProtectedRoute>
                    <YieldInput />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/crop-management"
                element={
                  <ProtectedRoute>
                    <CropManagement />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/calendar"
                element={
                  <ProtectedRoute>
                    <CropCalendar />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/irrigation"
                element={
                  <ProtectedRoute>
                    <Irrigation />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                }
              />
            </Routes>
          </main>
          <Footer />
          <AuthModal />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
