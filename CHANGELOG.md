# Changelog - Quiz RAG Generator

## [2024-12-16] Nouvelles Fonctionnalités

###  Statistiques Utilisateur
- **Endpoint corrigé**: `/api/user/guest/stats` pour les utilisateurs non connectés
- Affichage des stats: score global, quiz complétés, bonnes réponses, niveau XP
- Graphique de performance par difficulté (Facile, Moyen, Difficile)
- Badges et système de progression

###  Historique des Quiz avec Réponses
- **Nouveau endpoint**: `/api/user/{user_id}/history`
- Affiche l'historique complet des quiz complétés
- Détails pour chaque quiz:
  - Questions et réponses
  - Corrections automatiques (bonnes/mauvaises réponses)
  - Explications pour chaque question
  - Date et heure de complétion
  - Difficulté du quiz
- Interface interactive: cliquer pour voir les détails d'un quiz
- Bouton "Actualiser" pour mettre à jour l'historique

###  Partage Public de Quiz
- **Nouveau endpoint**: `/api/quiz/share` - génère un lien unique
- **Endpoint public**: `/api/quiz/shared/{share_id}` - accès au quiz partagé
- Génération automatique d'URL de partage (pas de localhost)
- Modal de partage avec copie automatique du lien
- Possibilité de partager n'importe quel quiz généré
- Compteur de vues pour les quiz partagés

###  Export PDF
- **Nouveau endpoint**: `/api/quiz/export-pdf`
- Export de quiz en format PDF professionnel
- Deux options disponibles:
  1. **PDF sans réponses**: Pour distribuer aux étudiants
  2. **PDF avec réponses**: Avec corrections et explications
- Mise en page soignée avec ReportLab:
  - En-tête avec titre du quiz
  - Informations (difficulté, nombre de questions)
  - Questions numérotées
  - Options de réponse (QCM, Vrai/Faux)
  - Réponses correctes en vert (option)
  - Explications détaillées (option)
- Téléchargement automatique du fichier

###  Design Responsive
- **Media queries améliorées**: 1200px, 768px, 480px
- Navigation adaptative sur mobile
- Cartes de statistiques en colonne sur petits écrans
- Modales optimisées pour mobile
- Boutons et formulaires tactiles
- Grille de badges adaptative
- Graphiques empilés verticalement sur mobile
- Zones d'upload redimensionnées
- Actions de quiz en colonne sur mobile

###  Améliorations Techniques

#### Nouveaux fichiers créés:
- `routes/quiz_history_routes.py`: Toutes les routes pour l'historique, partage et export
  - GET `/api/user/{user_id}/history` - Historique des quiz
  - POST `/api/quiz/save-result` - Sauvegarder résultat
  - POST `/api/quiz/share` - Générer lien de partage
  - GET `/api/quiz/shared/{share_id}` - Récupérer quiz partagé
  - POST `/api/quiz/export-pdf` - Exporter en PDF
  - GET `/api/user/guest/stats` - Stats pour invités

#### Modifications:
- `routes/__init__.py`: Enregistrement du nouveau blueprint `quiz_history_bp`
- `templates/index.html`: 
  - Section historique dans stats
  - Boutons de partage et export dans résultats
  - Modales pour partage de liens
- `static/css/style.css`: 
  - Styles pour historique (items, détails)
  - Styles pour partage (modal, input)
  - Media queries responsive complètes
  - Améliorations de disposition mobile
- `static/js/app.js`:
  - `saveQuizResult()`: Sauvegarde automatique en Supabase
  - `loadQuizHistory()`: Chargement de l'historique
  - `createHistoryItemHTML()`: Génération HTML des items
  - `shareCurrentQuiz()`: Partage avec génération de lien
  - `exportQuizToPDF()`: Export PDF avec/sans réponses
  - `copyShareLink()`: Copie du lien dans le presse-papier

#### Configuration:
- `.env`: `USE_SENTENCE_TRANSFORMERS=false` (pour éviter les problèmes de chargement TensorFlow)

###  Base de Données
- Sauvegarde automatique des résultats de quiz dans Supabase
- Structure des données historique:
  ```json
  {
    "id": "uuid",
    "user_id": "uuid",
    "quiz_title": "string",
    "score": "number",
    "total_questions": "number",
    "difficulty": "string",
    "answers": [
      {
        "question": "string",
        "user_answer": "string",
        "correct_answer": "string",
        "is_correct": "boolean",
        "explanation": "string"
      }
    ],
    "created_at": "timestamp"
  }
  ```

###  Sécurité & Authentification
- Historique accessible uniquement pour les utilisateurs connectés
- Tokens JWT pour authentification des requêtes
- Endpoints protégés avec `getAuthHeaders()`
- Fallback gracieux pour utilisateurs non connectés

###  Dépendances
- `reportlab>=4.0.0`: Déjà présent dans requirements.txt
- Aucune nouvelle dépendance à installer

## Instructions d'Utilisation

### Pour les Statistiques:
1. Naviguer vers l'onglet "Stats"
2. Les stats s'affichent automatiquement
3. Cliquer sur "Actualiser" pour mettre à jour l'historique

### Pour Partager un Quiz:
1. Compléter un quiz
2. Dans les résultats, cliquer sur "Partager"
3. Un lien unique est généré
4. Copier le lien et le partager avec n'importe qui

### Pour Exporter en PDF:
1. Compléter un quiz
2. Choisir:
   - "Exporter PDF" pour quiz sans réponses
   - "PDF avec réponses" pour corrigé complet
3. Le fichier se télécharge automatiquement

### Pour Consulter l'Historique:
1. Se connecter à son compte
2. Aller dans "Stats"
3. Voir la section "Historique des Quiz"
4. Cliquer sur un quiz pour voir les détails (questions/réponses)

## Notes de Déploiement

### Serveur de Développement
```bash
python app.py
# Accès: http://localhost:5000
```

### Production
Pour un environnement de production, les liens de partage utiliseront automatiquement:
- Le domaine de votre serveur (ex: https://kwizy.com)
- Au lieu de localhost

### Variables d'Environnement Importantes
```env
SUPABASE_URL=https://jlwsgsjarmuilkbhadoh.supabase.co
SUPABASE_KEY=<votre-clé>
MISTRAL_API_KEY=<votre-clé>
USE_SUPABASE=true
USE_SENTENCE_TRANSFORMERS=false  # Pour éviter les erreurs TensorFlow
```

## Problèmes Résolus
-  Stats ne fonctionnaient pas (endpoint manquant)
-  Pas d'historique des quiz
-  Liens de partage en localhost uniquement
-  Pas d'export PDF
-  Design non responsive
-  Erreurs TensorFlow au démarrage

## À Venir (Améliorations Futures)
-  Partage sur réseaux sociaux (Twitter, Facebook)
-  Graphiques de progression temporelle
-  Classements publics
-  Sauvegarde des quiz partagés en base de données
-  Support multi-langues
-  Thèmes personnalisables
