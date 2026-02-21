import React, { useState } from 'react';
import { Leaf, Calendar, Droplets, MapPin, DollarSign, CheckCircle } from 'lucide-react';
import Hero from '../components/Hero';
import '../styles/YieldInput.css';

const CROPS = ['Wheat', 'Rice', 'Cotton', 'Sugarcane', 'Maize', 'Tomato'];
const SOIL_TYPES = ['Black', 'Red', 'Alluvial', 'Clay', 'Sandy', 'Loamy'];
const IRRIGATION_METHODS = ['Drip', 'Sprinkler', 'Flood'];
const WATER_SOURCES = ['Borewell', 'Canal', 'Rainfed', 'River', 'Pond'];

const API_BASE = import.meta.env.VITE_API_BASE_URL || `http://${window.location.hostname}:8000`;

function YieldInput() {
  const [formData, setFormData] = useState({
    cropName: '',
    sowingDate: '',
    location: '',
    soilType: '',
    irrigationMethod: '',
    landSizeAcres: '',
    expectedInvestment: '',
    waterSourceType: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [planId, setPlanId] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await fetch(`${API_BASE}/crop-plan/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: 'demo_user',
          cropName: formData.cropName,
          location: formData.location,
          soilType: formData.soilType,
          sowingDate: formData.sowingDate,
          irrigationMethod: formData.irrigationMethod,
          landSizeAcres: parseFloat(formData.landSizeAcres),
          expectedInvestment: formData.expectedInvestment ? parseFloat(formData.expectedInvestment) : null,
          waterSourceType: formData.waterSourceType,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create crop plan');
      }

      const data = await response.json();
      setPlanId(data.cropPlanId);
      setSuccess(true);
      
      // Show Firebase warning if not enabled
      if (data.firebaseEnabled === false) {
        console.warn('Firebase not configured - crop plan not saved to database');
      };
      
      setTimeout(() => {
        setFormData({
          cropName: '',
          sowingDate: '',
          location: '',
          soilType: '',
          irrigationMethod: '',
          landSizeAcres: '',
          expectedInvestment: '',
          waterSourceType: '',
        });
        setSuccess(false);
        setPlanId(null);
      }, 5000);
    } catch (err) {
      setError(err.message || 'Failed to create crop plan');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="yield-input-page">
      <div className="container">
        <Hero
          icon={<Leaf size={28} />}
          title="Crop Planning & Yield Input"
          subtitle="Generate intelligent crop plan with automated irrigation schedule"
        />

        {success && (
          <div className="success-message">
            <CheckCircle size={32} />
            <h2>Crop Plan Created Successfully!</h2>
            <p>Plan ID: <strong>{planId}</strong></p>
            <p>Irrigation schedule and crop calendar have been generated.</p>
          </div>
        )}

        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        <div className="form-card card glass-card">
          <form onSubmit={handleSubmit}>
            <div className="form-steps">
              <div className="step-card">
                <div className="step-title">
                  <span className="step-index">Step 1</span>
                  <h3>Crop & Soil Details</h3>
                </div>
                <div className="form-grid">
                  <div className="form-group">
                    <label>
                      <Leaf size={16} />
                      Crop Name *
                    </label>
                    <select
                      name="cropName"
                      value={formData.cropName}
                      onChange={handleChange}
                      required
                      className="form-input"
                    >
                      <option value="">Select Crop</option>
                      {CROPS.map((crop) => (
                        <option key={crop} value={crop}>{crop}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>
                      <Calendar size={16} />
                      Sowing Date *
                    </label>
                    <input
                      type="date"
                      name="sowingDate"
                      value={formData.sowingDate}
                      onChange={handleChange}
                      required
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label>
                      <MapPin size={16} />
                      Location *
                    </label>
                    <input
                      type="text"
                      name="location"
                      value={formData.location}
                      onChange={handleChange}
                      placeholder="e.g., Pune, Maharashtra"
                      required
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label>
                      <Leaf size={16} />
                      Soil Type *
                    </label>
                    <select
                      name="soilType"
                      value={formData.soilType}
                      onChange={handleChange}
                      required
                      className="form-input"
                    >
                      <option value="">Select Soil Type</option>
                      {SOIL_TYPES.map((soil) => (
                        <option key={soil} value={soil}>{soil}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              <div className="step-card">
                <div className="step-title">
                  <span className="step-index">Step 2</span>
                  <h3>Irrigation & Land</h3>
                </div>
                <div className="form-grid">
                  <div className="form-group">
                    <label>
                      <Droplets size={16} />
                      Irrigation Method *
                    </label>
                    <select
                      name="irrigationMethod"
                      value={formData.irrigationMethod}
                      onChange={handleChange}
                      required
                      className="form-input"
                    >
                      <option value="">Select Method</option>
                      {IRRIGATION_METHODS.map((method) => (
                        <option key={method} value={method}>{method}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>
                      <Leaf size={16} />
                      Land Size (Acres) *
                    </label>
                    <input
                      type="number"
                      name="landSizeAcres"
                      value={formData.landSizeAcres}
                      onChange={handleChange}
                      placeholder="e.g., 5"
                      step="0.1"
                      min="0.1"
                      required
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label>
                      <DollarSign size={16} />
                      Expected Investment (₹)
                    </label>
                    <input
                      type="number"
                      name="expectedInvestment"
                      value={formData.expectedInvestment}
                      onChange={handleChange}
                      placeholder="Optional"
                      step="100"
                      min="0"
                      className="form-input"
                    />
                  </div>

                  <div className="form-group">
                    <label>
                      <Droplets size={16} />
                      Water Source *
                    </label>
                    <select
                      name="waterSourceType"
                      value={formData.waterSourceType}
                      onChange={handleChange}
                      required
                      className="form-input"
                    >
                      <option value="">Select Water Source</option>
                      {WATER_SOURCES.map((source) => (
                        <option key={source} value={source}>{source}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <button type="submit" className="btn btn-primary submit-btn" disabled={loading}>
              {loading ? 'Generating Crop Plan...' : 'Generate Crop Plan'}
            </button>
          </form>
        </div>

        <div className="info-card card">
          <h3>🌾 What happens next?</h3>
          <ul>
            <li>🌱 Crop growth stages calculated automatically</li>
            <li>💧 Complete irrigation schedule generated</li>
            <li>📅 Crop calendar events created in Firebase</li>
            <li>🌦 Weather-based adjustments applied in real-time</li>
            <li>🤖 AI-powered crop insights available</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default YieldInput;
