# Quiz RAG Generator - Kwizy

Système intelligent de génération de quiz basé sur RAG (Retrieval-Augmented Generation) utilisant Flask et Mistral AI.

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Démarrage](#démarrage)
- [Utilisation](#utilisation)
- [API](#api)
- [Structure des fichiers](#structure-des-fichiers)
- [Sécurité](#sécurité)
- [Dépannage](#dépannage)
- [Contribution](#contribution)

## Fonctionnalités

### Gestion des Documents
- Upload de documents multiples : PDF, PPTX, DOCX, TXT, RTF, PNG, JPG, JPEG
- Extraction intelligente du texte de tous types de documents
- Traitement batch et gestion des fichiers volumineux

### Système RAG
- Chunking intelligent et recherche sémantique
- ChromaDB pour le stockage vectoriel
- Récupération de contexte pertinent pour la génération de questions

### Génération de Quiz Personnalisée
- **Niveaux de difficulté** : Facile, Moyen, Difficile
- **Types de questions** :
  - QCM (Choix Multiple)
  - Compréhension
  - Mémorisation
  - Vrai/Faux
  - Réponse Courte
- **Paramétrisation** :
  - Nombre de questions (1-50)
  - Format de réponses personnalisé
  - Explications détaillées

### Gestion Utilisateur
- Authentification Supabase
- Préférences utilisateur (thème, langue, profil, mode notification, mode étude)
- Historique des quiz
- Statistiques personnalisées

### Gamification
- Système de points XP
- Badges et achievements
- Classements
- Streaks de révision

### Features Avancées
- Partage de quiz avec lien unique
- Export PDF avec/sans réponses
- Flashcards avec spaced repetition
- Collaboration et classrooms (pour les enseignants)
- Analytics et tableaux de bord

## Architecture

```
quiz-generate/
├── app.py                          # Entrée principale Flask
├── config.py                       # Configuration de l'application
├── requirements.txt                # Dépendances Python
│
├── models/                         # Modèles de base de données
│   ├── user.py                    # Modèle utilisateur
│   ├── document.py                # Modèle document
│   ├── quiz.py                    # Modèle quiz
│   ├── gamification.py            # Modèles achievements/badges
│   └── ...
│
├── services/                       # Logique métier
│   ├── supabase_service.py        # Authentification Supabase
│   ├── user_service.py            # Gestion utilisateur
│   ├── quiz_service.py            # Logique des quiz
│   ├── document_service.py        # Traitement documents
│   ├── gamification_service.py    # Système gamification
│   ├── analytics_service.py       # Analytics
│   └── ...
│
├── routes/                         # Points d'accès API
│   ├── user_routes.py             # Auth et profil utilisateur
│   ├── quiz_routes.py             # Endpoints quiz
│   ├── document_routes.py         # Upload et gestion documents
│   ├── gamification_routes.py     # Achievements et badges
│   └── ...
│
├── static/                         # Fichiers statiques
│   ├── css/
│   │   └── style.css              # Styles principaux
│   └── js/
│       └── app.js                 # Logique frontend
│
├── templates/                      # Templates HTML
│   └── index.html                 # Page principale
│
├── tests/                          # Tests unitaires et intégration
│   ├── test_quiz_generator.py
│   ├── test_rag_system.py
│   ├── test_routes.py
│   └── ...
│
└── chroma_db/                      # Base vectorielle (ChromaDB)
```

## Prérequis

- Python 3.9+
- Node.js (optionnel, pour le frontend)
- Clé API Mistral [console.mistral.ai](https://console.mistral.ai)
- (Optionnel) Compte Supabase pour authentification

## Installation

### 1. Cloner le projet

```bash
git clone https://github.com/YoussefChlih/Kwizy.git
cd Kwizy
```

### 2. Créer un environnement virtuel

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

## Configuration

### Variables d'environnement

Créer un fichier `.env` à la racine du projet:

```bash
# Flask
SECRET_KEY=your-secret-key-here
DEBUG=False

# Mistral AI
MISTRAL_API_KEY=your-mistral-api-key

# Supabase (optionnel)
USE_SUPABASE=false
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key

# Fichiers
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# Base de données
DATABASE_URL=sqlite:///quiz_app.db

# Feature flags
USE_SENTENCE_TRANSFORMERS=false  # Éviter les erreurs TensorFlow
```

## Démarrage

### Mode développement

```bash
python app.py
```

L'application sera disponible sur: http://localhost:5000

### Mode production

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Utilisation

### Upload de documents

1. Allez sur l'accueil
2. Cliquez sur "Upload"
3. Sélectionnez un ou plusieurs fichiers
4. Attendez l'extraction du texte

### Générer un quiz

1. Allez dans "Quiz"
2. Sélectionnez les options :
   - Nombre de questions (1-50)
   - Niveau de difficulté
   - Types de questions
3. Cliquez sur "Générer"
4. Répondez aux questions

### Consulter l'historique

1. Allez dans "Stats"
2. Consultez vos résultats précédents
3. Cliquez sur un résultat pour voir le détail

## API

### Authentification

```
POST /api/auth/register
POST /api/auth/login
GET /api/auth/me
POST /api/auth/logout
```

### Documents

```
GET /api/documents
POST /api/upload
DELETE /api/documents/<id>
```

### Quiz

```
GET /api/quiz
POST /api/quiz/generate
GET /api/quiz/<id>
POST /api/quiz/<id>/submit
GET /api/quiz/shared/<share_id>
POST /api/quiz/<id>/share
```

### Utilisateur

```
GET /api/user/preferences
PUT /api/user/preferences
GET /api/user/history
GET /api/user/stats
```

### Gamification

```
GET /api/badges
GET /api/achievements
GET /api/leaderboard
```

## Structure des fichiers

### Fichiers clés de configuration

- `config.py` : Configuration générale (clés API, paramètres de sécurité)
- `requirements.txt` : Dépendances Python
- `.env` : Variables d'environnement (ne pas committer)

### Code source principal

- `app.py` : Application Flask principale, initialisation
- `quiz_generator.py` : Classe pour générer les quiz
- `rag_system.py` : Système RAG avec ChromaDB et recherche sémantique
- `document_processor.py` : Extraction et traitement des documents

## Sécurité

### Points importants

1. **Ne pas exposer les clés API** :
   - Utiliser les variables d'environnement
   - Ne pas committer le `.env`
   - Ajouter `.env` au `.gitignore`

2. **Authentification** :
   - Tokens JWT pour chaque requête
   - Supabase pour l'authentification (optionnel)
   - Validation des tokens côté serveur

3. **Validation des données** :
   - Validation des uploads (extensions, taille)
   - Sanitisation des inputs utilisateur
   - Limitation des requêtes API

4. **CORS** :
   - Configuration restrictive pour la production
   - Domaines autorisés uniquement

## Dépannage

### Problème: Erreur Mistral API

**Solution**: Vérifier la clé API dans `.env`

```bash
# Tester la connexion
curl -X GET "https://api.mistral.ai/v1/models" \
  -H "Authorization: Bearer YOUR_KEY"
```

### Problème: ChromaDB non disponible

**Solution**: Réinstaller ChromaDB

```bash
pip install --upgrade chromadb
```

### Problème: Dépendances manquantes

**Solution**: Réinstaller toutes les dépendances

```bash
pip install -r requirements.txt --force-reinstall
```

### Problème: Port 5000 déjà utilisé

**Solution**: Utiliser un autre port

```bash
export FLASK_ENV=development
export FLASK_PORT=5001
python app.py
```

## Tests

### Lancer tous les tests

```bash
pytest
```

### Lancer les tests avec couverture

```bash
pytest --cov=. --cov-report=html
```

### Tests rapides seulement

```bash
pytest -m "not slow"
```

## Contribution

Les contributions sont bienvenues ! Pour contribuer:

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### Directives de contribution

- Respecter le style de code (PEP 8)
- Ajouter des tests pour les nouvelles fonctionnalités
- Mettre à jour la documentation
- Pas de dépendances non-documentées

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour les détails.

## Auteurs et remerciements

- **Youssef Chlih** - Développeur principal
- **Mistral AI** - Modèle IA pour la génération
- **Supabase** - Backend et authentification (optionnel)
- **ChromaDB** - Base vectorielle

## Support

Pour du support :
- Ouvrir une issue sur GitHub
- Consulter la documentation
- Vérifier les FAQ

---

Dernière mise à jour: 28 Décembre 2025
Version: 2.0.0
