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
  const [uploadingDoc, setUploadingDoc] = useState(false);
  const [generatingQuiz, setGeneratingQuiz] = useState(false);
  const [quizForm, setQuizForm] = useState({
    documentId: '',
    numQuestions: '10',
    difficulty: 'medium',
  });

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

  const handleDocumentUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploadingDoc(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      await documentsAPI.upload(formData);
      setError('');
      // Reload documents
      const docsResp = await documentsAPI.list();
      setDocuments(docsResp.data.documents || []);
    } catch (err) {
      setError('Upload failed: ' + (err.response?.data?.error || 'Unknown error'));
    } finally {
      setUploadingDoc(false);
    }
  };

  const handleGenerateQuiz = async (e) => {
    e.preventDefault();
    if (!quizForm.documentId) {
      setError('Please select a document');
      return;
    }

    setGeneratingQuiz(true);
    try {
      await quizAPI.generate({
        document_id: quizForm.documentId,
        num_questions: parseInt(quizForm.numQuestions),
        difficulty: quizForm.difficulty,
      });
      setError('');
      setQuizForm({ documentId: '', numQuestions: '10', difficulty: 'medium' });
      // Reload quizzes
      const quizzesResp = await quizAPI.getHistory();
      setQuizzes(quizzesResp.data.quizzes || []);
      alert('Quiz generated successfully!');
    } catch (err) {
      setError('Generate failed: ' + (err.response?.data?.error || 'Unknown error'));
    } finally {
      setGeneratingQuiz(false);
    }
  };

  const handleDeleteDocument = async (id) => {
    if (!window.confirm('Delete this document?')) return;
    try {
      await documentsAPI.delete(id);
      setDocuments(documents.filter(d => d.id !== id));
      setError('');
    } catch (err) {
      setError('Delete failed');
    }
  };

  if (loading) return <div className="dashboard-container"><p className="loading">Loading...</p></div>;

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-left">
          <h1>🎓 Kwizy</h1>
          <p>AI Quiz Generator</p>
        </div>
        <div className="header-right">
          <div className="user-info">
            <span className="user-name">{user?.first_name} {user?.last_name}</span>
            <span className="user-email">{user?.email}</span>
          </div>
          <button onClick={handleLogout} className="logout-button">Logout</button>
        </div>
      </header>

      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button onClick={() => setError('')}>✕</button>
        </div>
      )}

      <nav className="dashboard-nav">
        <button
          className={`nav-button ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          📊 Overview
        </button>
        <button
          className={`nav-button ${activeTab === 'quizzes' ? 'active' : ''}`}
          onClick={() => setActiveTab('quizzes')}
        >
          ❓ My Quizzes ({quizzes.length})
        </button>
        <button
          className={`nav-button ${activeTab === 'documents' ? 'active' : ''}`}
          onClick={() => setActiveTab('documents')}
        >
          📄 Documents ({documents.length})
        </button>
        <button
          className={`nav-button ${activeTab === 'generate' ? 'active' : ''}`}
          onClick={() => setActiveTab('generate')}
        >
          ✨ Generate Quiz
        </button>
      </nav>

      <main className="dashboard-main">
        {activeTab === 'dashboard' && (
          <section className="dashboard-overview">
            <div className="welcome-section">
              <h2>Welcome back, {user?.first_name}! 👋</h2>
              <p className="company-info">{user?.company && `Working at ${user?.company}`}</p>
            </div>
            
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-number">{quizzes.length}</div>
                <div className="stat-label">Quizzes Completed</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{documents.length}</div>
                <div className="stat-label">Documents</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">---</div>
                <div className="stat-label">Avg Score</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">---</div>
                <div className="stat-label">Learning Streak</div>
              </div>
            </div>

            <div className="quick-actions">
              <h3>Quick Actions</h3>
              <div className="action-buttons">
                <button 
                  onClick={() => setActiveTab('documents')}
                  className="action-btn"
                >
                  📤 Upload Document
                </button>
                <button 
                  onClick={() => setActiveTab('generate')}
                  className="action-btn"
                >
                  🚀 Generate Quiz
                </button>
              </div>
            </div>
          </section>
        )}

        {activeTab === 'quizzes' && (
          <section className="quizzes-section">
            <h2>📚 My Quizzes</h2>
            {quizzes.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">❓</div>
                <p>No quizzes yet. Create one to get started!</p>
                <button 
                  onClick={() => setActiveTab('generate')}
                  className="cta-button"
                >
                  Create Your First Quiz
                </button>
              </div>
            ) : (
              <div className="quiz-list">
                {quizzes.map(quiz => (
                  <div key={quiz.id} className="quiz-item">
                    <div className="quiz-header">
                      <h3>{quiz.title || 'Untitled Quiz'}</h3>
                      <span className={`difficulty ${quiz.difficulty}`}>
                        {quiz.difficulty}
                      </span>
                    </div>
                    <div className="quiz-details">
                      <span>❓ {quiz.questions_count || 0} questions</span>
                      <span>📅 {new Date(quiz.created_at).toLocaleDateString()}</span>
                    </div>
                    <button className="take-quiz-btn">Take Quiz →</button>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {activeTab === 'documents' && (
          <section className="documents-section">
            <h2>📄 My Documents</h2>
            
            <div className="upload-area">
              <label className="upload-label">
                <div className="upload-icon">📤</div>
                <p>Drag files here or click to upload</p>
                <span className="file-types">PDF, DOCX, PPTX, TXT, RTF, PNG, JPG</span>
                <input 
                  type="file" 
                  onChange={handleDocumentUpload}
                  disabled={uploadingDoc}
                  accept=".pdf,.docx,.pptx,.txt,.rtf,.png,.jpg,.jpeg"
                />
              </label>
              {uploadingDoc && <p className="uploading">Uploading...</p>}
            </div>

            {documents.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📄</div>
                <p>No documents uploaded yet.</p>
              </div>
            ) : (
              <div className="document-list">
                {documents.map(doc => (
                  <div key={doc.id} className="document-item">
                    <div className="doc-icon">📑</div>
                    <div className="doc-info">
                      <h3>{doc.title || 'Untitled'}</h3>
                      <p className="doc-meta">{doc.file_type} • {new Date(doc.created_at).toLocaleDateString()}</p>
                    </div>
                    <div className="doc-actions">
                      <button 
                        className="action-icon"
                        onClick={() => handleDeleteDocument(doc.id)}
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {activeTab === 'generate' && (
          <section className="generate-section">
            <h2>✨ Generate New Quiz</h2>
            
            {documents.length === 0 ? (
              <div className="generate-empty">
                <p>Upload a document first to generate a quiz</p>
                <button 
                  onClick={() => setActiveTab('documents')}
                  className="cta-button"
                >
                  Go to Documents
                </button>
              </div>
            ) : (
              <form onSubmit={handleGenerateQuiz} className="generate-form">
                <div className="form-group">
                  <label htmlFor="document">📄 Select Document</label>
                  <select 
                    id="document"
                    value={quizForm.documentId}
                    onChange={(e) => setQuizForm({...quizForm, documentId: e.target.value})}
                    className="form-input"
                  >
                    <option value="">Choose a document...</option>
                    {documents.map(doc => (
                      <option key={doc.id} value={doc.id}>{doc.title || 'Untitled'}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="questions">❓ Number of Questions</label>
                  <input 
                    id="questions"
                    type="number" 
                    min="1" 
                    max="50"
                    value={quizForm.numQuestions}
                    onChange={(e) => setQuizForm({...quizForm, numQuestions: e.target.value})}
                    className="form-input"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="difficulty">⚡ Difficulty Level</label>
                  <select 
                    id="difficulty"
                    value={quizForm.difficulty}
                    onChange={(e) => setQuizForm({...quizForm, difficulty: e.target.value})}
                    className="form-input"
                  >
                    <option value="easy">Easy - Perfect for beginners</option>
                    <option value="medium">Medium - Balanced difficulty</option>
                    <option value="hard">Hard - For experts</option>
                  </select>
                </div>

                <button 
                  type="submit" 
                  disabled={generatingQuiz}
                  className="submit-button"
                >
                  {generatingQuiz ? 'Generating... 🔄' : '🚀 Generate Quiz'}
                </button>
              </form>
            )}
          </section>
        )}
      </main>
    </div>
  );
}

export default Dashboard;
