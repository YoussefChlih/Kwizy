import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';
import '../styles/Auth.css';

function Auth() {
  const navigate = useNavigate();
  const [isSignup, setIsSignup] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    company: '',
  });

  const [passwordStrength, setPasswordStrength] = useState(0);
  const [showPassword, setShowPassword] = useState(false);

  // Redirect to dashboard if already authenticated
  useEffect(() => {
    if (localStorage.getItem('isAuthenticated') === 'true') {
      navigate('/dashboard', { replace: true });
    }
  }, [navigate]);

  const validateEmail = (email) => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  };

  const calculatePasswordStrength = (pwd) => {
    let strength = 0;
    if (pwd.length >= 8) strength += 25;
    if (pwd.length >= 12) strength += 25;
    if (/[A-Z]/.test(pwd)) strength += 25;
    if (/[0-9]/.test(pwd)) strength += 25;
    if (/[!@#$%^&*]/.test(pwd)) strength += 25;
    return Math.min(strength, 100);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });

    if (name === 'password') {
      setPasswordStrength(calculatePasswordStrength(value));
    }
  };

  const validateForm = () => {
    if (!formData.email || !formData.password) {
      setError('Email and password are required');
      return false;
    }

    if (!validateEmail(formData.email)) {
      setError('Please enter a valid email');
      return false;
    }

    if (isSignup) {
      if (!formData.firstName || !formData.lastName) {
        setError('First and last names are required');
        return false;
      }
      if (formData.password.length < 8) {
        setError('Password must be at least 8 characters');
        return false;
      }
      if (formData.password !== formData.confirmPassword) {
        setError('Passwords do not match');
        return false;
      }
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!validateForm()) return;

    setLoading(true);
    try {
      if (isSignup) {
        const response = await authAPI.signup({
          email: formData.email,
          password: formData.password,
          first_name: formData.firstName,
          last_name: formData.lastName,
          company: formData.company || null,
        });
        if (response.data?.user) {
          localStorage.setItem('user', JSON.stringify(response.data.user));
          localStorage.setItem('isAuthenticated', 'true');
        }
        setSuccess('Signup successful! Redirecting to dashboard...');
        setTimeout(() => navigate('/dashboard'), 2000);
      } else {
        const response = await authAPI.login({
          email: formData.email,
          password: formData.password,
        });
        if (response.data?.user) {
          localStorage.setItem('user', JSON.stringify(response.data.user));
          localStorage.setItem('isAuthenticated', 'true');
        }
        setSuccess('Login successful! Redirecting to dashboard...');
        setTimeout(() => navigate('/dashboard'), 2000);
      }
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Authentication failed';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const getPasswordStrengthText = () => {
    if (passwordStrength === 0) return '';
    if (passwordStrength <= 25) return 'Weak';
    if (passwordStrength <= 50) return 'Fair';
    if (passwordStrength <= 75) return 'Good';
    return 'Strong';
  };

  const getPasswordStrengthColor = () => {
    if (passwordStrength === 0) return 'transparent';
    if (passwordStrength <= 25) return '#ef4444';
    if (passwordStrength <= 50) return '#f59e0b';
    if (passwordStrength <= 75) return '#3b82f6';
    return '#10b981';
  };

  return (
    <div className="auth-container">
      <div className="auth-background">
        <div className="blob blob-1"></div>
        <div className="blob blob-2"></div>
      </div>

      <div className="auth-card">
        <div className="auth-header">
          <h1>🎓 Kwizy</h1>
          <p>AI-Powered Quiz Generation Platform</p>
        </div>

        <div className="auth-toggle">
          <button
            className={`toggle-btn ${!isSignup ? 'active' : ''}`}
            onClick={() => {
              setIsSignup(false);
              setError('');
              setSuccess('');
              setFormData({ firstName: '', lastName: '', email: '', password: '', confirmPassword: '', company: '' });
            }}
          >
            🔐 Login
          </button>
          <button
            className={`toggle-btn ${isSignup ? 'active' : ''}`}
            onClick={() => {
              setIsSignup(true);
              setError('');
              setSuccess('');
              setFormData({ firstName: '', lastName: '', email: '', password: '', confirmPassword: '', company: '' });
            }}
          >
            ✍️ Sign Up
          </button>
        </div>

        {error && (
          <div className="alert alert-error">
            <span>❌ {error}</span>
          </div>
        )}

        {success && (
          <div className="alert alert-success">
            <span>✅ {success}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          {isSignup && (
            <>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="firstName">First Name</label>
                  <input
                    id="firstName"
                    type="text"
                    name="firstName"
                    value={formData.firstName}
                    onChange={handleInputChange}
                    placeholder="John"
                    className="form-input"
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="lastName">Last Name</label>
                  <input
                    id="lastName"
                    type="text"
                    name="lastName"
                    value={formData.lastName}
                    onChange={handleInputChange}
                    placeholder="Doe"
                    className="form-input"
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="company">Company (Optional)</label>
                <input
                  id="company"
                  type="text"
                  name="company"
                  value={formData.company}
                  onChange={handleInputChange}
                  placeholder="Your Company"
                  className="form-input"
                />
              </div>
            </>
          )}

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              placeholder="you@example.com"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">
              Password
              {isSignup && formData.password && (
                <span className="password-strength">
                  Strength: <strong style={{ color: getPasswordStrengthColor() }}>
                    {getPasswordStrengthText()}
                  </strong>
                </span>
              )}
            </label>
            <div className="password-input-wrapper">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="••••••••"
                className="form-input"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="password-toggle"
              >
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
            {isSignup && formData.password && (
              <div className="strength-bar">
                <div
                  className="strength-fill"
                  style={{
                    width: `${passwordStrength}%`,
                    backgroundColor: getPasswordStrengthColor(),
                  }}
                ></div>
              </div>
            )}
          </div>

          {isSignup && (
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                id="confirmPassword"
                type={showPassword ? 'text' : 'password'}
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                placeholder="••••••••"
                className="form-input"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="submit-button"
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                {isSignup ? 'Creating Account...' : 'Logging in...'}
              </>
            ) : (
              isSignup ? '✍️ Create Account' : '🔐 Log In'
            )}
          </button>
        </form>

        <div className="auth-footer">
          <p className="terms-text">
            By using Kwizy, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>
      </div>
    </div>
  );
}

export default Auth;
