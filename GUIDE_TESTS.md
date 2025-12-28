# Guide d'Utilisation des Tests - Quiz RAG Generator

## 📋 Table des Matières

- [Vue d'ensemble](#vue-densemble)
- [Exécution des Tests](#exécution-des-tests)
  - [Windows (PowerShell)](#windows-powershell)
  - [Linux/Mac (Bash)](#linuxmac-bash)
- [Modes d'Exécution](#modes-dexécution)
- [Options Disponibles](#options-disponibles)
- [Exemples d'Utilisation](#exemples-dutilisation)
- [Rapports Générés](#rapports-générés)
- [Organisation des Tests](#organisation-des-tests)

## 🎯 Vue d'ensemble

Le projet dispose de deux scripts pour exécuter les tests :
- **`run_tests.ps1`** : Pour Windows (PowerShell)
- **`run_tests.sh`** : Pour Linux/Mac (Bash)

Ces scripts offrent des paramètres flexibles pour personnaliser l'exécution des tests selon vos besoins.

## 🚀 Exécution des Tests

### Windows (PowerShell)

#### Exécution Simple
```powershell
.\run_tests.ps1
```

#### Afficher l'aide
```powershell
.\run_tests.ps1 -Help
```

#### Exemples
```powershell
# Tests rapides uniquement
.\run_tests.ps1 -Mode rapide

# Tests d'intégration avec verbosité élevée
.\run_tests.ps1 -Mode integration -Verbosity 2

# Tests sur un fichier spécifique
.\run_tests.ps1 -File tests\test_config.py

# Tests avec mot-clé sans couverture
.\run_tests.ps1 -Keyword "upload" -NoCov

# Tests en parallèle
.\run_tests.ps1 -Parallel 4

# Générer tous les formats de rapports
.\run_tests.ps1 -Xml -Json
```

### Linux/Mac (Bash)

#### Rendre le script exécutable (première fois)
```bash
chmod +x run_tests.sh
```

#### Exécution Simple
```bash
./run_tests.sh
```

#### Afficher l'aide
```bash
./run_tests.sh --help
```

#### Exemples
```bash
# Tests rapides uniquement
./run_tests.sh -m rapide

# Tests d'intégration avec verbosité élevée
./run_tests.sh -m integration -v 2

# Tests sur un fichier spécifique
./run_tests.sh -f tests/test_config.py

# Tests avec mot-clé sans couverture
./run_tests.sh -k "upload" --no-cov

# Tests en parallèle
./run_tests.sh -p 4

# Générer tous les formats de rapports
./run_tests.sh --xml --json
```

## 📊 Modes d'Exécution

### Mode `rapide` (par défaut pour développement)
Exécute uniquement les tests unitaires rapides, en excluant les tests d'intégration et les tests lents.

**Quand l'utiliser :**
- Développement quotidien
- Avant de commiter du code
- Pour une feedback rapide

**Exemple :**
```powershell
.\run_tests.ps1 -Mode rapide
```

### Mode `complet` (par défaut)
Exécute tous les tests disponibles sans distinction.

**Quand l'utiliser :**
- Avant de créer une pull request
- Tests de validation complète
- CI/CD pipeline

**Exemple :**
```powershell
.\run_tests.ps1 -Mode complet
```

### Mode `integration`
Exécute uniquement les tests d'intégration marqués avec `@pytest.mark.integration`.

**Quand l'utiliser :**
- Vérification de l'intégration entre composants
- Tests de bout en bout
- Validation du système complet

**Exemple :**
```powershell
.\run_tests.ps1 -Mode integration
```

### Mode `slow`
Exécute uniquement les tests lents marqués avec `@pytest.mark.slow`.

**Quand l'utiliser :**
- Tests de performance
- Tests de charge
- Tests nécessitant beaucoup de ressources

**Exemple :**
```powershell
.\run_tests.ps1 -Mode slow
```

## ⚙️ Options Disponibles

### Verbosité (`-Verbosity` / `-v`)

| Niveau | Description | Utilisation |
|--------|-------------|-------------|
| 0 | Minimal | Affiche uniquement les résumés |
| 1 | Normal | Verbosité standard (par défaut) |
| 2 | Détaillé | Affiche les détails des tests |
| 3 | Très détaillé | Affiche tous les détails et logs |

**Exemple :**
```powershell
.\run_tests.ps1 -Verbosity 3
```

### Fichier Spécifique (`-File` / `-f`)

Exécute un seul fichier de test.

**Exemple :**
```powershell
.\run_tests.ps1 -File tests\test_quiz_generator.py
```

### Filtres par Mot-clé (`-Keyword` / `-k`)

Exécute uniquement les tests dont le nom contient le mot-clé spécifié.

**Exemple :**
```powershell
# Exécuter tous les tests contenant "upload"
.\run_tests.ps1 -Keyword "upload"

# Exécuter tous les tests contenant "config" ou "rag"
.\run_tests.ps1 -Keyword "config or rag"
```

### Parallélisation (`-Parallel` / `-p`)

Exécute les tests en parallèle avec N workers pour accélérer l'exécution.

**Note :** Nécessite le package `pytest-xdist` (inclus dans requirements.txt)

**Exemple :**
```powershell
# Utiliser 4 workers
.\run_tests.ps1 -Parallel 4
```

### Options de Rapports

| Option | Description |
|--------|-------------|
| `-NoHtml` / `--no-html` | Désactive le rapport HTML |
| `-Xml` / `--xml` | Génère un rapport XML (format JUnit) |
| `-Json` / `--json` | Génère un rapport JSON |
| `-NoCov` / `--no-cov` | Désactive la couverture de code |

**Exemple :**
```powershell
# Générer rapport XML et JSON sans HTML
.\run_tests.ps1 -NoHtml -Xml -Json
```

## 📝 Exemples d'Utilisation

### Développement Quotidien
```powershell
# Tests rapides avec verbosité normale
.\run_tests.ps1 -Mode rapide
```

### Avant un Commit Git
```powershell
# Tests complets avec verbosité détaillée
.\run_tests.ps1 -Mode complet -Verbosity 2
```

### Debugging d'un Test Spécifique
```powershell
# Exécuter un seul fichier avec verbosité maximale
.\run_tests.ps1 -File tests\test_rag_system.py -Verbosity 3
```

### Test d'une Fonctionnalité Spécifique
```powershell
# Filtrer par mot-clé
.\run_tests.ps1 -Keyword "document_processor"
```

### CI/CD Pipeline
```powershell
# Tests complets avec rapports XML pour intégration continue
.\run_tests.ps1 -Mode complet -Xml -Parallel 4
```

### Vérification Rapide Sans Couverture
```powershell
# Tests rapides sans génération de couverture
.\run_tests.ps1 -Mode rapide -NoCov
```

## 📊 Rapports Générés

Tous les rapports sont générés dans le dossier `reports/` à la racine du projet.

### Rapport HTML de Tests
- **Emplacement :** `reports/test_report.html`
- **Contenu :** 
  - Vue d'ensemble des tests exécutés
  - Status de chaque test (✓ passed, ✗ failed)
  - Logs et tracebacks détaillés
  - Durée d'exécution

**Ouvrir le rapport :**
```powershell
# Windows
start reports\test_report.html

# Linux/Mac
open reports/test_report.html
```

### Rapport de Couverture
- **Emplacement :** `reports/coverage/index.html`
- **Contenu :**
  - Pourcentage de couverture par fichier
  - Lignes couvertes vs non couvertes
  - Vue détaillée du code avec annotations
  - Branches couvertes

**Ouvrir le rapport :**
```powershell
# Windows
start reports\coverage\index.html

# Linux/Mac
open reports/coverage/index.html
```

### Rapport XML (JUnit)
- **Emplacement :** `reports/test_report.xml`
- **Utilisation :** Intégration avec CI/CD (Jenkins, GitLab CI, etc.)
- **Format :** Standard JUnit XML

### Rapport JSON
- **Emplacement :** `reports/test_report.json`
- **Utilisation :** Analyse personnalisée, dashboards
- **Contenu :** Données structurées des résultats de tests

## 🗂️ Organisation des Tests

```
tests/
├── conftest.py                    # Configuration pytest et fixtures
├── test_config.py                 # Tests de configuration
├── test_document_processor.py     # Tests du traitement de documents
├── test_quiz_generator.py         # Tests de génération de quiz
├── test_rag_system.py            # Tests du système RAG
├── test_routes.py                # Tests des routes API
└── test_integration.py           # Tests d'intégration
```

### Marqueurs de Tests

Les tests peuvent être marqués avec des décorateurs pytest :

```python
import pytest

# Test lent
@pytest.mark.slow
def test_long_operation():
    pass

# Test d'intégration
@pytest.mark.integration
def test_full_workflow():
    pass
```

## 🔧 Configuration Pytest

Le fichier `pytest.ini` contient la configuration par défaut :

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --html=reports/test_report.html
    --self-contained-html
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

## 📈 Bonnes Pratiques

### 1. Tests Rapides en Développement
```powershell
.\run_tests.ps1 -Mode rapide
```

### 2. Tests Complets Avant Pull Request
```powershell
.\run_tests.ps1 -Mode complet -Verbosity 2
```

### 3. Vérifier la Couverture
```powershell
.\run_tests.ps1
# Puis ouvrir: reports\coverage\index.html
```

### 4. Tester une Fonctionnalité Spécifique
```powershell
.\run_tests.ps1 -Keyword "nom_de_la_fonctionnalité"
```

### 5. Parallélisation pour Gagner du Temps
```powershell
.\run_tests.ps1 -Parallel 4
```

## 🐛 Debugging

### Test qui échoue
```powershell
# Exécuter le test avec verbosité maximale
.\run_tests.ps1 -File tests\test_failing.py -Verbosity 3 -NoCov
```

### Voir les logs complets
Ouvrir `reports\test_report.html` et cliquer sur le test en échec pour voir le traceback complet.

## 🔗 Ressources

- [Documentation Pytest](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [pytest-html](https://pytest-html.readthedocs.io/)
- [pytest-xdist](https://pytest-xdist.readthedocs.io/) (parallélisation)

## ❓ FAQ

### Comment exécuter un seul test ?
```powershell
.\run_tests.ps1 -File tests\test_config.py -Keyword "test_specific_function"
```

### Comment désactiver temporairement un test ?
Utilisez le décorateur `@pytest.mark.skip` :
```python
@pytest.mark.skip(reason="Temporairement désactivé")
def test_something():
    pass
```

### Comment voir les logs pendant l'exécution ?
```powershell
.\run_tests.ps1 -Verbosity 3
```

### Les tests sont trop lents, comment accélérer ?
```powershell
# Utiliser le mode rapide
.\run_tests.ps1 -Mode rapide -Parallel 4
```

### Comment générer uniquement un rapport de couverture ?
```powershell
pytest tests/ --cov=. --cov-report=html:reports/coverage
```
