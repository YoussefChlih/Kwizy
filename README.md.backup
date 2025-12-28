# Quiz RAG Generator

Un système intelligent de génération de quiz basé sur RAG (Retrieval-Augmented Generation) utilisant Flask et Mistral AI.

##  Fonctionnalités

- **Upload de documents multiples** : PDF, PPTX, DOCX, TXT, RTF
- **Extraction intelligente** : Extraction automatique du texte de tous types de documents
- **RAG System** : Chunking et recherche sémantique pour un contexte pertinent
- **Génération de quiz personnalisée** :
  - **Niveaux de difficulté** : Facile, Moyen, Difficile
  - **Types de questions** :
    - QCM (Choix Multiple)
    - Compréhension
    - Mémorisation
    - Vrai/Faux
    - Réponse Courte
- **Interface web moderne** : Interface utilisateur intuitive et responsive
- **Export** : Exportez vos quiz en format Markdown

## Prérequis

- Python 3.9+
- Clé API Mistral (obtenir sur [console.mistral.ai](https://console.mistral.ai))

##  Installation

1. **Cloner ou naviguer vers le projet**
   ```bash
   cd quiz-rag-system
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement**
   ```bash
   # Copier le fichier exemple
   copy .env.example .env
   
   # Éditer .env et ajouter votre clé API Mistral
   MISTRAL_API_KEY=votre_cle_api_mistral
   SECRET_KEY=une_cle_secrete_pour_flask
   ```

##  Démarrage

```bash
python app.py
```

L'application sera disponible sur `http://localhost:5000`

##  Utilisation

### 1. Upload de Documents
- Glissez-déposez vos fichiers ou cliquez pour parcourir
- Formats supportés : PDF, PPTX, DOCX, TXT, RTF
- Les documents sont automatiquement traités et indexés

### 2. Configuration du Quiz
- **Nombre de questions** : 1 à 20 questions
- **Difficulté** :
  - *Facile* : Questions simples et directes
  - *Moyen* : Compréhension approfondie requise
  - *Difficile* : Analyse et réflexion critique
- **Types de questions** : Sélectionnez un ou plusieurs types
- **Sujet spécifique** (optionnel) : Focalisez sur un thème particulier

### 3. Quiz
- Répondez aux questions générées
- Vérifiez vos réponses pour voir les corrections
- Exportez le quiz en Markdown

##  Architecture

```
quiz-rag-system/
├── app.py                  # Application Flask principale
├── config.py               # Configuration
├── document_processor.py   # Traitement des documents
├── rag_system.py          # Système RAG (chunking, embeddings, search)
├── quiz_generator.py      # Génération de quiz avec Mistral
├── requirements.txt       # Dépendances Python
├── .env.example          # Exemple de configuration
├── templates/
│   └── index.html        # Template HTML principal
├── static/
│   ├── css/
│   │   └── style.css     # Styles CSS
│   └── js/
│       └── app.js        # JavaScript frontend
└── uploads/              # Dossier pour les fichiers uploadés
```

##  API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/health` | Vérification de l'état |
| GET | `/api/options` | Options de quiz disponibles |
| POST | `/api/upload` | Upload de document |
| GET | `/api/documents` | Stats des documents chargés |
| POST | `/api/documents/clear` | Supprimer tous les documents |
| POST | `/api/generate-quiz` | Générer un quiz |
| POST | `/api/search` | Rechercher dans les documents |

##  Exemple de requête API

```python
import requests

# Upload d'un document
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/upload',
        files={'file': f}
    )
    print(response.json())

# Génération de quiz
response = requests.post(
    'http://localhost:5000/api/generate-quiz',
    json={
        'num_questions': 5,
        'difficulty': 'moyen',
        'question_types': ['qcm', 'vrai_faux'],
        'topic': 'Machine Learning'  # optionnel
    }
)
print(response.json())
```

##  Sécurité

- Les fichiers uploadés sont stockés avec des noms uniques
- Validation des types de fichiers
- Limite de taille de fichier (16 MB par défaut)

##  Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

##  Licence

MIT License

##  Remerciements

- [Mistral AI](https://mistral.ai) pour l'API de génération
- [Sentence Transformers](https://www.sbert.net/) pour les embeddings
- [FAISS](https://github.com/facebookresearch/faiss) pour la recherche vectorielle
