import React, { useState, useEffect } from 'react';
import { X, User, Layers, TrendingUp, Crop, Plus, Minus } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import '../styles/EditProfileModal.css';

// Custom stepper input replacing the native number spinner
const NumberInput = ({ name, value, onChange, placeholder, min = 0, step = 1 }) => {
  const numVal = value === '' ? '' : parseFloat(value);

  const adjust = (delta) => {
    const current = numVal === '' ? 0 : numVal;
    const next = Math.max(min, parseFloat((current + delta).toFixed(10)));
    onChange({ target: { name, value: String(next) } });
  };

  return (
    <div className="ep-number-wrapper">
      <button type="button" className="ep-stepper" onClick={() => adjust(-step)} tabIndex={-1}>
        <Minus size={13} />
      </button>
      <input
        type="number"
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        min={min}
        step={step}
        className="ep-number-input"
      />
      <button type="button" className="ep-stepper" onClick={() => adjust(step)} tabIndex={-1}>
        <Plus size={13} />
      </button>
    </div>
  );
};

const EditProfileModal = () => {
  const { user, updateUser, showEditProfile, setShowEditProfile } = useAuth();

  const [form, setForm] = useState({
    username: '',
    land_owned_acres: '',
    land_in_use_acres: '',
    revenue: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Populate form whenever the modal opens
  useEffect(() => {
    if (showEditProfile && user) {
      setForm({
        username: user.username || '',
        land_owned_acres: user.land_owned_acres ?? '',
        land_in_use_acres: user.land_in_use_acres ?? '',
        revenue: user.revenue ?? '',
      });
      setError('');
      setSuccess('');
    }
  }, [showEditProfile, user]);

  if (!showEditProfile) return null;

  const handleChange = (e) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
    setError('');
    setSuccess('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    // Validate land_in_use <= land_owned
    const owned = parseFloat(form.land_owned_acres);
    const inUse = parseFloat(form.land_in_use_acres);
    if (!isNaN(owned) && !isNaN(inUse) && inUse > owned) {
      setError('Land in use cannot exceed land owned.');
      setLoading(false);
      return;
    }

    try {
      const payload = {};
      if (form.username.trim() && form.username !== user.username)
        payload.username = form.username.trim();
      if (form.land_owned_acres !== '')
        payload.land_owned_acres = parseFloat(form.land_owned_acres);
      if (form.land_in_use_acres !== '')
        payload.land_in_use_acres = parseFloat(form.land_in_use_acres);
      if (form.revenue !== '')
        payload.revenue = parseFloat(form.revenue);

      await updateUser(payload);
      setSuccess('Profile updated successfully!');
      setTimeout(() => setShowEditProfile(false), 1200);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ep-overlay" onClick={() => setShowEditProfile(false)}>
      <div className="ep-modal" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="ep-header">
          <div className="ep-header-left">
            <div className="ep-avatar">{user?.username?.charAt(0).toUpperCase()}</div>
            <div>
              <h2>Edit Profile</h2>
              <p>{user?.email}</p>
            </div>
          </div>
          <button className="ep-close" onClick={() => setShowEditProfile(false)}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="ep-form">
          {/* Username */}
          <div className="ep-field">
            <label><User size={15} /> Username</label>
            <input
              name="username"
              value={form.username}
              onChange={handleChange}
              placeholder="Your username"
              autoComplete="off"
            />
          </div>

          <div className="ep-divider">Farm Details</div>

          {/* Land Owned */}
          <div className="ep-field">
            <label><Layers size={15} /> Land Ownership (acres)</label>
            <NumberInput
              name="land_owned_acres"
              value={form.land_owned_acres}
              onChange={handleChange}
              placeholder="Total land owned"
              min={0}
              step={0.5}
            />
          </div>

          {/* Land in Use */}
          <div className="ep-field">
            <label><Crop size={15} /> Land Currently in Use (acres)</label>
            <NumberInput
              name="land_in_use_acres"
              value={form.land_in_use_acres}
              onChange={handleChange}
              placeholder="Land actively farmed"
              min={0}
              step={0.5}
            />
          </div>

          {/* Revenue */}
          <div className="ep-field">
            <label><TrendingUp size={15} /> Annual Revenue / Investment (₹)</label>
            <NumberInput
              name="revenue"
              value={form.revenue}
              onChange={handleChange}
              placeholder="e.g. 500000"
              min={0}
              step={1000}
            />
          </div>

          {error && <p className="ep-error">{error}</p>}
          {success && <p className="ep-success">{success}</p>}

          <div className="ep-actions">
            <button type="button" className="ep-btn-cancel" onClick={() => setShowEditProfile(false)}>
              Cancel
            </button>
            <button type="submit" className="ep-btn-save" disabled={loading}>
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditProfileModal;
