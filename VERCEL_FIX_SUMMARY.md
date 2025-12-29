# Solution: Erreur "Resource not found" sur Vercel

## Problème Identifié

Quand vous déployez sur Vercel, le frontend React reçoit l'erreur:
```
{"error":"Resource not found","success":false}
```

Cela signifie que les requêtes API ne trouvent pas le backend.

## Causes Principales

1. **Configuration Vercel incorrecte** - Routes mal définies
2. **API URL non configurée** - Frontend ne sait pas où appeler le backend
3. **CORS non compatible** - Origins hardcodés pour localhost

## Solutions Appliquées

### 1. Mis à jour `vercel.json`

Le nouveau `vercel.json` configure correctement:
- Frontend React buildé en statique
- Backend API sur `/api/*` routes
- Routes SPA pour React (rewrite 404 vers index.html)

```json
"routes": [
  { "src": "/api/(.*)", "dest": "app.py" },           // API routes
  { "src": "/(.*\\.(?:js|css|...))$", "dest": "..." }, // Static assets
  { "src": "/(.*)", "dest": "frontend/build/index.html" } // SPA fallback
]
```

### 2. Amélioré `frontend/src/services/api.js`

Détecte automatiquement l'URL API:
- **Dev (localhost):** `http://localhost:5000`
- **Prod (Vercel):** Même domaine (`window.location.origin`)

```javascript
const getAPIURL = () => {
  if (process.env.REACT_APP_API_URL) return process.env.REACT_APP_API_URL;
  if (localhost) return 'http://localhost:5000';
  return window.location.origin; // Même domaine en prod
};
```

### 3. Configuré CORS dans `app.py`

Détecte si production ou développement:
- **Dev:** CORS restreint à localhost
- **Prod:** CORS ouvert (car même domaine)

```python
is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('VERCEL') == '1'
cors_origins = ['*'] if is_production else ['http://localhost:...']
```

### 4. Créé `frontend/.env.production`

Configure l'API URL pour la production:
```
REACT_APP_API_URL=https://your-domain.vercel.app
```

### 5. Créé `frontend/.env.local`

Configure l'API URL pour développement local:
```
REACT_APP_API_URL=http://localhost:5000
```

## Comment Déployer Maintenant

### Option 1: Frontend et Backend Séparés (RECOMMANDÉ)

**Plus simple et mieux supporté par Vercel.**

#### A. Frontend React
1. Sur Vercel, créer projet avec dossier root = `frontend/`
2. Framework: React
3. Build: `npm run build`
4. Environment: `REACT_APP_API_URL=https://your-api-url.vercel.app`
5. Deploy

#### B. Backend Flask
1. Sur Vercel, créer projet avec dossier root = `.`
2. Framework: Other
3. Build: `pip install -r requirements.txt`
4. Environment: `FLASK_ENV=production`, `SUPABASE_URL=...`, etc.
5. Deploy

#### C. Mettre à jour Frontend
Après avoir l'URL backend en prod:
1. Modifier `frontend/.env.production`
2. Mettre la vraie URL backend
3. Re-deploy frontend

**URLs Finales:**
- Frontend: `https://kwizy-frontend.vercel.app`
- Backend: `https://kwizy-backend.vercel.app`

### Option 2: Monorepo sur Vercel

Utilisez le `vercel.json` configuré (plus complexe).

## Tester Localement

```bash
# Terminal 1: Backend
FLASK_ENV=development python app.py
# localhost:5000

# Terminal 2: Frontend  
cd frontend
REACT_APP_API_URL=http://localhost:5000 npm start
# localhost:3000
```

Ou utilisez `api-tester.html` depuis le navigateur pour tester les endpoints.

## Si ça ne fonctionne toujours pas

1. **Vérifier les logs Vercel:**
   - Dashboard > Deployments > Function Logs (backend)
   - Vérifier les erreurs

2. **Tester l'API directement:**
   ```bash
   curl https://your-api-url.vercel.app/api/health
   ```

3. **Vérifier CORS:**
   - Ouvrir DevTools (F12)
   - Onglet Network
   - Regarder les réponses des requests API
   - Chercher "Access-Control-Allow-Origin"

4. **Vérifier Environment Variables:**
   - Vercel Dashboard > Settings > Environment Variables
   - Vérifier que SUPABASE_URL, etc. sont définis

## Architecture Finale

```
Vercel (Frontend)
http://your-app.vercel.app
    ↓ /api/*
Vercel (Backend)
http://your-api.vercel.app
    ↓
Supabase (Database)
```

---

**Fichiers Modifiés:**
- `vercel.json` - Configuration Vercel
- `frontend/src/services/api.js` - Auto-detection API URL
- `app.py` - CORS dynamique
- `frontend/.env.production` - Config production
- `frontend/.env.local` - Config développement
- `VERCEL_DEPLOYMENT.md` - Guide complet
- `api-tester.html` - Outil de test
