# Connexion Frontend → Backend → Base de Données

## Architecture

```
React Frontend (localhost:3000)
        ↓ HTTP REST API
Python Flask Backend (localhost:5000)
        ↓ Supabase Client
Supabase PostgreSQL Database
```

**Important:** Le frontend NE se connecte PAS directement à la base de données. Il passe par le backend API.

---

## Étapes de Configuration

### 1. Vérifier Configuration Backend (CRITIQUE)

**File: `.env` (à la racine du projet)**

```bash
# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_service_role_key

# Other
MISTRAL_API_KEY=your_api_key
FLASK_ENV=development
```

**Obtenir les clés:**
1. Allez sur https://supabase.com
2. Ouvrez votre projet
3. Allez à **Settings > API**
4. Copier:
   - `Project URL` → SUPABASE_URL
   - `service_role` secret → SUPABASE_KEY (PAS la clé anonyme!)

**Vérifier la connexion:**
```bash
python -c "from config import Config; print('✓ Supabase configuré' if Config.SUPABASE_URL else '✗ Supabase manquant')"
```

### 2. Vérifier Routes API Backend

**File: `app.py` et `routes/`**

Routes disponibles:
```
POST   /api/auth/signup           - Créer compte
POST   /api/auth/login            - Se connecter
GET    /api/auth/logout           - Se déconnecter
GET    /api/auth/profile          - Récupérer profil

POST   /api/documents/upload      - Upload document
GET    /api/documents             - Lister documents
POST   /api/documents/clear       - Supprimer tous

POST   /api/quiz/generate         - Générer quiz
GET    /api/quiz/history          - Historique quiz

GET    /api/health                - Vérifier santé
```

**Tester une route:**
```bash
curl http://localhost:5000/api/health
# Devrait retourner: {"status":"healthy",...}
```

### 3. Configurer Frontend pour Développement

**File: `frontend/.env.local`**

```dotenv
REACT_APP_API_URL=http://localhost:5000
```

**Fichier déjà configuré correctement.**

### 4. Configurer Frontend pour Production

**File: `frontend/.env.production`**

```dotenv
REACT_APP_API_URL=https://your-backend-url.com
REACT_APP_API_BASE=/api
```

**À faire:**
- Remplacer `your-backend-url.com` par l'URL réelle de votre backend en production

### 5. Vérifier Composants React

**File: `frontend/src/components/Auth.jsx`**

Doit appeler l'API via le service:
```javascript
import { authAPI } from '../services/api';

// Dans le formulaire
const handleSignup = async (data) => {
  const response = await authAPI.signup(data);
  // response.data.success = true si succès
};
```

**File: `frontend/src/components/Dashboard.jsx`**

Doit appeler les endpoints quiz et documents:
```javascript
import { quizAPI, documentsAPI } from '../services/api';

// Upload document
const handleUpload = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await documentsAPI.upload(formData);
};

// Générer quiz
const handleGenerateQuiz = async (options) => {
  const response = await quizAPI.generate(options);
};
```

### 6. Tester Localement

**Terminal 1: Backend**
```bash
cd quiz-generate
python app.py
# Attendez: "Running on http://localhost:5000"
```

**Terminal 2: Frontend**
```bash
cd quiz-generate/frontend
npm start
# Attendez: "Compiled successfully"
# S'ouvre à http://localhost:3000
```

**Tester le flow:**
1. Allez à http://localhost:3000
2. Cliquez "Sign Up"
3. Remplissez le formulaire
4. Vérifiez les logs du backend
5. Vous devriez voir "✓ Signup successful"

---

## Checklist de Configuration

### Backend
- [ ] `.env` créé avec SUPABASE_URL et SUPABASE_KEY
- [ ] `requirements.txt` installé (`pip install -r requirements.txt`)
- [ ] Flask démarre sans erreur
- [ ] `/api/health` retourne 200 et JSON
- [ ] Supabase accessible (vérifier SUPABASE_KEY est la clé service_role)

### Database (Supabase)
- [ ] Tables créées (auth.users, profiles, documents, etc.)
- [ ] RLS policies configurées
- [ ] Migrations appliquées (`supabase_migration_fix.sql`)
- [ ] Service role a les permissions nécessaires

### Frontend
- [ ] `frontend/.env.local` configuré avec URL backend dev
- [ ] `frontend/.env.production` configuré avec URL backend prod
- [ ] `npm install` exécuté dans `frontend/`
- [ ] `frontend/src/services/api.js` utilise les bonnes URLs
- [ ] React démarre sans erreur

### Connexion Frontend-Backend
- [ ] Backend écoute sur http://localhost:5000
- [ ] Frontend utilise http://localhost:5000 en dev
- [ ] CORS configuré (déjà fait dans `app.py`)
- [ ] Requête POST /api/auth/signup fonctionne

---

## Si ça ne Fonctionne Pas

### Erreur: "Cannot connect to backend"

```bash
# Vérifier backend écoute
curl http://localhost:5000/api/health

# Si erreur: backend n'est pas lancé
python app.py
```

### Erreur: "CORS policy blocked"

Vérifiez dans `app.py`:
```python
CORS(app, origins=['http://localhost:3000', ...], supports_credentials=True)
```

### Erreur: "Supabase error: missing credentials"

```bash
# Vérifier .env
cat .env | grep SUPABASE

# Doit retourner:
# SUPABASE_URL=https://xxxxx.supabase.co
# SUPABASE_KEY=your_service_role_key
```

### Erreur: "Profile not found" au signup

Cela signifie Supabase est connecté mais:
1. Table `profiles` n'existe pas
2. Ou RLS policies bloquent l'insertion

**Solution:**
```bash
# Exécuter la migration SQL
# Allez sur Supabase > SQL Editor
# Copier-coller: supabase_migration_fix.sql
# Exécuter
```

---

## Flux Complet d'une Requête

### Signup Flow:
```
1. User remplit formulaire signup
   ↓
2. Frontend: authAPI.signup(data)
   ↓
3. Axios envoie POST http://localhost:5000/api/auth/signup
   ↓
4. Backend: auth_routes.py reçoit la requête
   ↓
5. auth_service.py crée user dans Supabase
   ↓
6. Supabase auth.users table mise à jour
   ↓
7. auth_service.py crée profil dans profiles table
   ↓
8. Backend retourne: {"success": true, "message": "..."}
   ↓
9. Frontend reçoit réponse et redirige
```

### Upload Document Flow:
```
1. User sélectionne fichier
   ↓
2. Frontend: documentsAPI.upload(formData)
   ↓
3. Axios envoie POST http://localhost:5000/api/documents/upload
   ↓
4. Backend: document_routes.py reçoit le fichier
   ↓
5. document_processor.py extrait le texte
   ↓
6. rag_system.py ajoute à ChromaDB (vector store)
   ↓
7. Backend retourne: {"success": true, "file_id": "..."}
   ↓
8. Frontend affiche succès
```

---

## Prochaines Étapes

1. **Vérifier .env backend**
   ```bash
   cat .env
   ```

2. **Lancer backend**
   ```bash
   python app.py
   ```

3. **Lancer frontend**
   ```bash
   cd frontend && npm start
   ```

4. **Tester signup**
   - Allez à http://localhost:3000
   - Signup avec email/password
   - Vérifiez les logs

5. **Déployer**
   - Quand tout fonctionne localement
   - Déployer backend (Vercel/Railway)
   - Déployer frontend (Vercel)
   - Configurer `.env.production`

---

## Questions Fréquentes

**Q: Le frontend peut-il se connecter directement à Supabase?**
A: Non, c'est un risque de sécurité. Supabase expose les clés publiques, donc utilisez toujours le backend comme intermédiaire.

**Q: Où sont stockés les documents?**
A: Dans le dossier `uploads/` (local) et dans ChromaDB (vector embeddings pour la recherche RAG).

**Q: Où est stocké l'authentification?**
A: Dans Supabase (auth.users et profiles tables).

**Q: Quel est le langage de requête pour la BD?**
A: PostgreSQL (via Supabase). Les requêtes vont par Supabase Python client.

---

## Support

- `VERCEL_DEPLOYMENT.md` - Guide déploiement Vercel
- `VERCEL_FIX_SUMMARY.md` - Solutions erreurs Vercel
- `FIX_AUTHENTICATION.md` - Guide authentification
- `api-tester.html` - Tester les endpoints directement
