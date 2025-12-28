import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

// Authentication
export const authAPI = {
  signup: (data) => api.post('/api/auth/signup', data),
  login: (data) => api.post('/api/auth/login', data),
  logout: () => api.post('/api/auth/logout'),
  getProfile: () => api.get('/api/auth/profile'),
  updateProfile: (data) => api.put('/api/auth/profile', data),
  checkSession: () => api.get('/api/auth/check-session'),
  forgotPassword: (data) => api.post('/api/auth/forgot-password', data),
};

// Quiz
export const quizAPI = {
  generate: (data) => api.post('/api/quiz/generate', data),
  getHistory: () => api.get('/api/quiz/history'),
  getQuiz: (id) => api.get(`/api/quiz/${id}`),
  submitAttempt: (id, data) => api.post(`/api/quiz/${id}/attempt`, data),
};

// Documents
export const documentsAPI = {
  upload: (formData) => api.post('/api/documents/upload', formData),
  list: () => api.get('/api/documents'),
  delete: (id) => api.delete(`/api/documents/${id}`),
};

// Health
export const healthAPI = {
  check: () => api.get('/api/health'),
};

export default api;
