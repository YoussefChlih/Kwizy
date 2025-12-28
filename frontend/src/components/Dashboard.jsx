import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI, quizAPI, documentsAPI } from '../services/api';
import '../styles/Dashboard.css';

function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [quizzes, setQuizzes] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      // Check session
      const sessionResp = await authAPI.checkSession();
      if (!sessionResp.data.logged_in) {
        navigate('/auth');
        return;
      }

      // Get profile
      const profileResp = await authAPI.getProfile();
      setUser(profileResp.data.profile);

      // Get quizzes and documents
      const quizzesResp = await quizAPI.getHistory();
      setQuizzes(quizzesResp.data.quizzes || []);

      const docsResp = await documentsAPI.list();
      setDocuments(docsResp.data.documents || []);

      setError('');
    } catch (err) {
      setError('Failed to load dashboard');
      setTimeout(() => navigate('/auth'), 2000);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      navigate('/auth');
    } catch (err) {
      setError('Logout failed');
    }
  };

  if (loading) return <div className="dashboard-container"><p>Loading...</p></div>;

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-left">
          <h1>Kwizy</h1>
        </div>
        <div className="header-right">
          <span className="user-name">{user?.first_name} {user?.last_name}</span>
          <button onClick={handleLogout} className="logout-button">Logout</button>
        </div>
      </header>

      {error && <div className="error-message">{error}</div>}

      <nav className="dashboard-nav">
        <button
          className={`nav-button ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          Overview
        </button>
        <button
          className={`nav-button ${activeTab === 'quizzes' ? 'active' : ''}`}
          onClick={() => setActiveTab('quizzes')}
        >
          My Quizzes
        </button>
        <button
          className={`nav-button ${activeTab === 'documents' ? 'active' : ''}`}
          onClick={() => setActiveTab('documents')}
        >
          Documents
        </button>
        <button
          className={`nav-button ${activeTab === 'generate' ? 'active' : ''}`}
          onClick={() => setActiveTab('generate')}
        >
          Generate Quiz
        </button>
      </nav>

      <main className="dashboard-main">
        {activeTab === 'dashboard' && (
          <section className="dashboard-overview">
            <h2>Welcome, {user?.first_name}!</h2>
            <div className="stats-grid">
              <div className="stat-card">
                <h3>{quizzes.length}</h3>
                <p>Quizzes Completed</p>
              </div>
              <div className="stat-card">
                <h3>{documents.length}</h3>
                <p>Documents</p>
              </div>
              <div className="stat-card">
                <h3>---</h3>
                <p>Avg Score</p>
              </div>
            </div>
          </section>
        )}

        {activeTab === 'quizzes' && (
          <section className="quizzes-section">
            <h2>My Quizzes</h2>
            {quizzes.length === 0 ? (
              <p className="empty-state">No quizzes yet. Create one to get started!</p>
            ) : (
              <div className="quiz-list">
                {quizzes.map(quiz => (
                  <div key={quiz.id} className="quiz-item">
                    <h3>{quiz.title}</h3>
                    <p>{quiz.questions_count} questions • {quiz.difficulty}</p>
                    <p className="date">{new Date(quiz.created_at).toLocaleDateString()}</p>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {activeTab === 'documents' && (
          <section className="documents-section">
            <h2>My Documents</h2>
            {documents.length === 0 ? (
              <p className="empty-state">No documents uploaded yet.</p>
            ) : (
              <div className="document-list">
                {documents.map(doc => (
                  <div key={doc.id} className="document-item">
                    <h3>{doc.title}</h3>
                    <p>{doc.file_type}</p>
                    <p className="date">{new Date(doc.created_at).toLocaleDateString()}</p>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {activeTab === 'generate' && (
          <section className="generate-section">
            <h2>Generate New Quiz</h2>
            <form className="generate-form">
              <select className="form-input" defaultValue="">
                <option value="">Select Document</option>
                {documents.map(doc => (
                  <option key={doc.id} value={doc.id}>{doc.title}</option>
                ))}
              </select>
              <input type="number" placeholder="Number of Questions" min="1" max="50" className="form-input" />
              <select className="form-input" defaultValue="medium">
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
              <button type="submit" className="submit-button">Generate Quiz</button>
            </form>
          </section>
        )}
      </main>
    </div>
  );
}

export default Dashboard;
