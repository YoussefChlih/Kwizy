import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';
import '../styles/Auth.css';

function Auth() {
  const navigate = useNavigate();
  const [isSignup, setIsSignup] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    firstName: '',
    lastName: '',
    company: '',
    jobTitle: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const validatePassword = (password) => {
    if (password.length < 8) return 'Min 8 characters';
    if (!/[A-Z]/.test(password)) return 'Needs uppercase letter';
    if (!/[0-9]/.test(password)) return 'Needs digit';
    return '';
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setError('');

    const passwordError = validatePassword(formData.password);
    if (passwordError) {
      setError(passwordError);
      return;
    }

    setLoading(true);
    try {
      await authAPI.signup({
        email: formData.email,
        password: formData.password,
        first_name: formData.firstName,
        last_name: formData.lastName,
        company: formData.company || '',
        job_title: formData.jobTitle || '',
        language: 'en',
      });
      setError('');
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');

    setLoading(true);
    try {
      await authAPI.login({
        email: formData.email,
        password: formData.password,
      });
      setError('');
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Kwizy</h1>
          <p>Quiz Generator with AI</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={isSignup ? handleSignup : handleLogin} className="auth-form">
          {isSignup && (
            <>
              <input
                type="text"
                name="firstName"
                placeholder="First Name"
                value={formData.firstName}
                onChange={handleChange}
                required
              />
              <input
                type="text"
                name="lastName"
                placeholder="Last Name"
                value={formData.lastName}
                onChange={handleChange}
                required
              />
              <input
                type="text"
                name="company"
                placeholder="Company (optional)"
                value={formData.company}
                onChange={handleChange}
              />
              <input
                type="text"
                name="jobTitle"
                placeholder="Job Title (optional)"
                value={formData.jobTitle}
                onChange={handleChange}
              />
            </>
          )}

          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
          />

          <button
            type="submit"
            disabled={loading}
            className="auth-button"
          >
            {loading ? 'Loading...' : isSignup ? 'Sign Up' : 'Sign In'}
          </button>
        </form>

        <p className="auth-toggle">
          {isSignup ? 'Already have account? ' : "Don't have account? "}
          <button
            type="button"
            onClick={() => {
              setIsSignup(!isSignup);
              setError('');
              setFormData({ email: '', password: '', firstName: '', lastName: '', company: '', jobTitle: '' });
            }}
            className="toggle-button"
          >
            {isSignup ? 'Sign In' : 'Sign Up'}
          </button>
        </p>
      </div>
    </div>
  );
}

export default Auth;
