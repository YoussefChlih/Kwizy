# Kwizy - Project Structure

## Architecture

Le projet est maintenant organisé en architecture 3-tier:

```
Kwizy/
├── Frontend (React)          - localhost:3000
│   └── frontend/
│
├── Backend API (Python)      - localhost:5000
│   ├── app.py
│   ├── auth_service.py
│   ├── auth_routes.py
│   ├── rag_system.py
│   ├── quiz_generator.py
│   ├── document_processor.py
│   ├── config.py
│   ├── models/               - SQLAlchemy models
│   ├── routes/               - API blueprints
│   └── services/             - Business logic
│
└── Database                  - Supabase (PostgreSQL)
    └── Cloud-hosted
```

## Dossiers Supprimés

Les éléments suivants ont été supprimés (interface Python):

- ~~`templates/`~~ - Templates HTML Flask (frontend React remplace cela)
- ~~`static/`~~ - Fichiers statiques Flask (frontend React remplace cela)
- ~~`test_auth_flow.py`~~ - Script test Python
- ~~`test_supabase_direct.py`~~ - Script test Python
- ~~`verify_auth.py`~~ - Script vérification Python
- ~~`hi.py`~~ - Fichier test

## Architecture Finale

### Frontend - React (localhost:3000)

```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── Auth.jsx          - Login/Signup UI
│   │   ├── Dashboard.jsx      - Main interface
│   │   └── ...
│   ├── App.js
│   └── index.js
├── package.json
└── vercel.json               - Deployment config
```

Communication avec backend via HTTP REST API.

### Backend - Flask API (localhost:5000)

```
api/
├── Core Files:
│   ├── app.py                - Flask app (API only)
│   ├── config.py             - Configuration
│   ├── wsgi.py               - WSGI entry point
│
├── Authentication:
│   ├── auth_service.py       - Auth logic
│   ├── auth_routes.py        - Auth endpoints
│
├── Document Processing:
│   ├── document_processor.py - PDF/Doc processing
│   ├── rag_system.py         - RAG vector search
│   ├── quiz_generator.py     - Quiz generation
│
├── Database:
│   ├── models/               - Pydantic/SQLAlchemy models
│   ├── models/__init__.py    - DB initialization
│   └── models/*.py           - Entity definitions
│
├── API Routes:
│   ├── routes/__init__.py    - Blueprint registration
│   ├── routes/user_routes.py
│   ├── routes/quiz_routes.py
│   ├── routes/document_routes.py
│   ├── routes/flashcard_routes.py
│   └── ...
│
├── Business Logic:
│   ├── services/             - Service classes
│   ├── services/__init__.py
│   ├── services/auth_service.py (refactor)
│   └── ...
│
└── Utilities:
    ├── requirements.txt      - Dependencies
    ├── pytest.ini            - Test configuration
    └── chroma_db/            - Vector store
```

API endpoints uniquement - Aucune route web.

### Database - Supabase PostgreSQL

Tables principales:
- `auth.users` - Authentification Supabase
- `profiles` - Profils utilisateur
- `documents` - Documents uploadés
- `quizzes` - Quiz générés
- `quiz_history` - Historique utilisateur
- `activity_logs` - Logs
- Et autres tables de domaine

## API Endpoints

### Authentification
```
POST   /api/auth/signup
POST   /api/auth/login
GET    /api/auth/logout
POST   /api/auth/refresh
GET    /api/auth/profile/:id
```

### Documents
```
POST   /api/documents/upload
GET    /api/documents
POST   /api/documents/clear
```

### Quizzes
```
POST   /api/generate-quiz
GET    /api/quizzes
POST   /api/quiz/:id/submit
```

### Santé
```
GET    /api/health
```

## Fichiers de Configuration

### .env (Ne pas commit)
```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_service_role_key
MISTRAL_API_KEY=your_mistral_key
FLASK_ENV=development
```

### Fichiers Git
```
.gitignore      - Ignore __pycache__, .env, uploads, etc.
.env.example    - Template pour .env
```

## Technologies

### Frontend
- React 18.2
- Axios (HTTP client)
- CSS (gradients modernes)
- Vercel (deployment)

### Backend
- Flask 2.x (API framework)
- SQLAlchemy (ORM)
- Supabase Python client
- ChromaDB (vector store)
- SentenceTransformers (embeddings)
- Mistral API (LLM)

### Database
- PostgreSQL (via Supabase)
- Row Level Security (RLS)
- Realtime capabilities

## Mode de Déploiement

### Développement Local
```bash
# Terminal 1: Backend Flask
python app.py
# http://localhost:5000

# Terminal 2: Frontend React
cd frontend
npm start
# http://localhost:3000
```

### Production
- **Frontend**: Vercel (React)
- **Backend**: Vercel Serverless / Cloud Run / Heroku (Flask)
- **Database**: Supabase (PostgreSQL)

## Points Clés

✓ Interface Web Python supprimée
✓ Frontend React indépendant
✓ Backend API Python pur (sans routes web)
✓ Communication REST API
✓ Authentification Supabase
✓ Prêt pour déploiement cloud

## Résumé des Changements

| Aspect | Avant | Après |
|--------|-------|-------|
| Frontend | Templates Flask | React (localhost:3000) |
| Backend | API + Web routes | API seulement |
| Interface | Flask web | React UI |
| Structure | Monolith Flask | Microservices API |
| Déploiement | Single server | Frontend + Backend séparés |

---

**Architecture Finale**: Frontend React + Backend API + Database Cloud  
**Sans**: Interface web Python, templates, fichiers statiques
