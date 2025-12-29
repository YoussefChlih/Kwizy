# Déploiement sur Vercel - Guide Complet

## Architecture Recommandée

Pour Vercel, il y a 2 options:

### Option 1: Frontend et Backend Séparés (RECOMMANDÉ)

**Frontend React:**
- Repository: Déployer le dossier `frontend/` seul sur Vercel
- URL: `https://kwizy-frontend.vercel.app`

**Backend Flask:**
- Repository: Déployer le root seul sur Vercel (ou autre service)
- URL: `https://kwizy-backend.vercel.app`

### Option 2: Monorepo sur Vercel (Plus complexe)

Nécessite une configuration `vercel.json` spéciale.

---

## Option 1: Déploiement Séparé (RECOMMANDÉ)

### A. Frontend React sur Vercel

**Step 1:** Sur Vercel Dashboard, créer nouveau project

**Step 2:** Selectionner votre repo GitHub

**Step 3:** Configuration:
- **Root Directory:** `frontend/`
- **Framework:** React
- **Build Command:** `npm run build`
- **Output Directory:** `build`

**Step 4:** Environment Variables:
```
REACT_APP_API_URL=https://votre-backend-url.com
```

**Step 5:** Deploy

### B. Backend Flask sur Vercel

**Step 1:** Sur Vercel, créer nouveau project pour le backend

**Step 2:** Configuration:
- **Root Directory:** `.` (root du repo)
- **Framework:** Other
- **Build Command:** `pip install -r requirements.txt`
- **Output Directory:** (laisser vide)

**Step 3:** Environment Variables:
```
FLASK_ENV=production
SUPABASE_URL=...
SUPABASE_KEY=...
MISTRAL_API_KEY=...
```

**Step 4:** Deploy

### C. Configurer Frontend pour parler au Backend

Après avoir les URLs:

**frontend/.env.production:**
```
REACT_APP_API_URL=https://votre-backend.vercel.app
```

Re-deploy le frontend.

---

## Option 2: Monorepo sur Vercel

Utilisez le `vercel.json` configuré dans la racine du projet.

**Limitations:**
- Frontend doit être buildé et mis en statique
- Configuration plus complexe
- Plus difficile à maintenir

---

## Problèmes Courants et Solutions

### Erreur: "Resource not found" (404)

**Cause:** 
- Frontend ne trouve pas le backend
- Routes API mal configurées
- CORS non configuré

**Solution:**
```javascript
// Dans api.js du frontend:
const API_URL = window.location.origin; // Utilise même domaine en prod
```

### Erreur: "CORS policy blocked"

**Cause:** CORS non activé sur backend

**Solution:** Backend Flask doit avoir:
```python
CORS(app, origins=['*'], supports_credentials=True)
```

### Erreur: "/api/..." endpoints return 404

**Cause:** Frontend pointe vers mauvaise URL

**Solution:** Vérifier:
1. `REACT_APP_API_URL` en `.env.production`
2. Endpoints commencent par `/api/`
3. Backend écoute sur bon port

---

## Déploiement Recommandé

### Option Meilleure: Frontend sur Vercel + Backend sur Railway/Render

**Frontend:** Vercel (free tier excellent)
**Backend:** Railway ou Render (free tier avec limitations)
**Database:** Supabase (free tier)

Configuration simple, scalable, gratuit.

---

## Commandes pour Tester Localement

```bash
# Terminal 1: Backend
FLASK_ENV=development python app.py
# Sur http://localhost:5000

# Terminal 2: Frontend
cd frontend
REACT_APP_API_URL=http://localhost:5000 npm start
# Sur http://localhost:3000
```

---

## Checklist Avant Deploy

- [ ] Frontend `.env.production` configuré avec URL backend
- [ ] Backend environment variables (SUPABASE_URL, etc.)
- [ ] CORS activé sur Flask
- [ ] Routes API commencent par `/api/`
- [ ] Database Supabase accessible (RLS configuré)
- [ ] `requirements.txt` à jour
- [ ] `package.json` à jour (frontend)
- [ ] `.gitignore` bien configuré

---

## Après Deploy

**Tester endpoints:**
```bash
# Depuis terminal ou Postman
curl https://votre-backend.vercel.app/api/health

# Depuis frontend console (F12)
fetch('https://votre-backend.vercel.app/api/health')
  .then(r => r.json())
  .then(d => console.log(d))
```

**Vérifier logs:**
- Vercel Dashboard > Deployments > Logs
- Frontend > Deployments > Function Logs (backend)
