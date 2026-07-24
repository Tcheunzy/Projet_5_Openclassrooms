# Projet 5 - Déploiement d'un modèle de Machine Learning

## Contexte

Freelance spécialisé en Machine Learning, mandaté par **Futurisys** pour rendre
opérationnel un modèle de prédiction du turnover des employés (départ volontaire
de l'entreprise) via une API de production.

Ce projet s'appuie sur le modèle développé lors du **Projet 4** (classification
binaire, prédiction du départ d'un salarié à partir de données RH).

## Objectifs

- Exposer le modèle de ML via une API REST (FastAPI)
- Garantir la fiabilité du code via des tests automatisés (Pytest)
- Assurer la traçabilité des prédictions via une base de données PostgreSQL
- Mettre en place un pipeline CI/CD (GitHub Actions + Render)
- Documenter l'ensemble du projet pour en assurer la maintenabilité

## Sommaire

- [Architecture du projet](#architecture-du-projet)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Base de données](#base-de-données)
- [Tests](#tests)
- [Déploiement](#déploiement)
- [Sécurité et authentification](#sécurité-et-authentification)
- [Workflow Git](#workflow-git)
- [Documentation complémentaire](#documentation-complémentaire)
- [Limites connues et améliorations possibles](#limites-connues-et-améliorations-possibles)

## Architecture du projet

\```
├── .github/workflows/  # Pipeline CI/CD (GitHub Actions)
├── api/                # API FastAPI (endpoints, schémas Pydantic)
│   └── routers/
├── data/                # Données brutes et traitées (non versionnées, sauf .gitkeep)
├── database/            # Connexion, modèles SQLAlchemy, script de création des tables
├── docs/                # Documentation technique complémentaire (schéma UML, model card)
├── models/              # Modèle de ML entraîné (model_pipeline.joblib, versionné)
├── notebooks/           # Notebook d'exploration et d'entraînement (Projet 4)
├── src/                 # Logique de prédiction, réutilisable indépendamment de l'API
├── tests/                # Tests unitaires et fonctionnels (Pytest)
├── Dockerfile            # Image de déploiement (Render)
├── .dockerignore
├── pyproject.toml        # Dépendances (équivalent requirements.txt, géré par uv)
└── README.md
\```

## Installation

### Prérequis
- Python 3.12
- [uv](https://docs.astral.sh/uv/) (gestionnaire de paquets Python)
- PostgreSQL (installation locale — voir section [Base de données](#base-de-données))
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (uniquement si vous voulez tester l'image de déploiement en local)

### Étapes

1. Cloner le dépôt
\```bash
git clone https://github.com/Tcheunzy/Projet_5_Openclassrooms.git
cd Projet_5_Openclassrooms
\```

2. Installer les dépendances (Python 3.12 sera installé automatiquement par `uv` si absent)
\```bash
uv python pin 3.12
uv sync
\```

3. Configurer les variables d'environnement
\```bash
cp .env.example .env
# Renseigner DATABASE_URL avec vos identifiants PostgreSQL locaux
\```

## Utilisation

### Lancer l'API en local

\```bash
uv run uvicorn api.main:app --reload
\```

L'API est alors disponible sur `http://127.0.0.1:8000`, avec une documentation
interactive Swagger générée automatiquement sur `http://127.0.0.1:8000/docs`.

### Endpoints disponibles

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/` | Vérifie que l'API est en ligne |
| `GET` | `/health` | Healthcheck (utilisé par les plateformes de déploiement) |
| `POST` | `/predict` | Prédit le risque de départ d'un employé et enregistre l'échange en base |

### Exemple d'appel à `/predict`

\```json
{
  "matricule": "4521",
  "employe": {
    "genre": "F",
    "statut_marital": "Célibataire",
    "poste": "Cadre Commercial",
    "domaine_etude": "Marketing",
    "frequence_deplacement": "Frequent",
    "age": 34,
    "annee_experience_totale": 8,
    "annees_dans_l_entreprise": 3,
    "...": "voir le schéma complet dans /docs (Swagger)"
  }
}
\```

Réponse :
\```json
{
  "probabilite_depart": 0.73,
  "prediction": 1,
  "label": "Démission",
  "seuil_utilise": 0.4
}
\```

L'ensemble des 28 champs attendus, leurs types et leurs contraintes de validation
sont documentés de façon interactive dans Swagger (`/docs`), avec un exemple
pré-rempli directement testable.

## Base de données

### Choix d'architecture

Deux tables normalisées :
- **`employes`** : état courant des données RH de chaque employé (une mise à jour
  écrase les anciennes valeurs).
- **`predictions`** : historique complet de chaque appel au modèle, avec un
  instantané JSON figé des données envoyées à ce moment précis (traçabilité
  complète même si les données de l'employé changent ensuite).

Le détail du raisonnement de conception et le schéma UML complet sont documentés
dans [`docs/schema_UML_BDD.md`](docs/schema_UML_BDD.md).

### Créer les tables en local

\```bash
psql -U postgres -c "CREATE DATABASE projet5;"
uv run python -m database.create_db
\```

> **Note :** conformément à l'énoncé du projet, l'interaction avec la base de
> données est prévue pour fonctionner **entièrement en local**. Voir la section
> [Limites connues](#limites-connues-et-améliorations-possibles) pour le
> comportement de l'API une fois déployée sur Render.

## Tests

### Lancer la suite de tests

\```bash
# Créer la base de test dédiée (une seule fois)
psql -U postgres -c "CREATE DATABASE projet5_test;"

# Lancer les tests
uv run pytest -v
\```

### Avec rapport de couverture

\```bash
uv run pytest --cov=src --cov=api --cov=database --cov-report=term-missing --cov-report=html
\```

Le rapport HTML détaillé est généré dans `htmlcov/index.html`.

### Composition de la suite (23 tests)

| Fichier | Portée | Nature |
|---|---|---|
| `tests/test_predict.py` | Logique de prédiction (`src/predict.py`) | Unitaire |
| `tests/test_schemas.py` | Validation Pydantic (`api/schemas.py`) | Unitaire |
| `tests/test_connection.py` | Connexion base de données | Unitaire |
| `tests/test_api.py` | Endpoints FastAPI, avec vraie base PostgreSQL de test | Fonctionnel |

Couverture actuelle : **100%** sur `api/`, `src/` et `database/` (le script
`database/create_db.py` est volontairement exclu du calcul : script d'entrée à
effet de bord, non pertinent à tester unitairement — voir `pyproject.toml`,
section `[tool.coverage.run]`).

## Déploiement

### Plateforme retenue : Render

Le projet ciblait initialement Hugging Face Spaces, mais Hugging Face a restreint
l'accès gratuit au SDK Docker en cours de projet. **[Render](https://render.com)**
a été retenu comme alternative équivalente et gratuite (build Docker,
déploiement automatique depuis GitHub, sans carte bancaire requise).

**URL de déploiement :** https://projet-5-openclassrooms.onrender.com

### Fonctionnement

- Render surveille la branche `main` du dépôt GitHub et redéploie automatiquement
  à chaque nouveau commit.
- Le déploiement s'appuie sur le `Dockerfile` à la racine du projet, qui installe
  uniquement les dépendances de production (`uv sync --frozen --no-dev`).

### Tester l'image Docker en local avant déploiement

\```bash
docker build -t projet5-api .
docker run -p 8000:8000 -e PORT=8000 projet5-api
\```

## Sécurité et authentification

### État actuel (POC)

Ce projet est un **Proof of Concept** et ne met pas en place d'authentification
sur l'API : les endpoints sont accessibles sans clé ni jeton. Ce choix est
assumé pour ce périmètre de projet, mais **ne serait pas acceptable en
production réelle**.

### Mesures de sécurité déjà en place

- **Secrets jamais committés** : `.env` est ignoré par Git (`.gitignore`),
  seul `.env.example` (gabarit sans valeur réelle) est versionné.
- **Validation stricte des entrées** : chaque champ de `/predict` est validé
  par Pydantic (types, bornes, valeurs autorisées) avant tout traitement,
  limitant les risques d'injection de données malformées.
- **HTTPS automatique** sur le déploiement Render (certificat TLS géré par
  la plateforme).
- **Intégrité référentielle en base** : contrainte `ForeignKey` PostgreSQL entre
  `predictions` et `employes`, empêchant les incohérences au niveau base
  elle-même (pas seulement applicatif).

### Ce qui serait nécessaire pour une mise en production réelle

- Authentification par clé d'API (header `X-API-Key`) ou OAuth2, selon les
  utilisateurs cibles de l'API.
- Chiffrement des données RH sensibles au repos (colonnes de `employes`).
- Limitation de débit (*rate limiting*) sur `/predict` pour éviter les abus.
- Journalisation et supervision (logs structurés, alerting).

## Workflow Git

### Modèle de branching

Ce projet suit une approche **GitHub Flow** (trunk-based simplifié) plutôt que
Git Flow : une seule branche longue durée (`main`, toujours stable et
déployable), et des branches courtes fusionnées via Pull Request après
validation de la CI. Choix adapté à un projet mono-développeur avec
déploiement continu, sans besoin de gérer plusieurs versions en parallèle.

### Convention de nommage des branches

| Préfixe | Usage |
|---|---|
| `main` | Code stable, déployé |
| `feature/<nom>` | Développement d'une nouvelle fonctionnalité |
| `fix/<nom>` | Correction de bug |
| `docs/<nom>` | Documentation uniquement |

### Convention de commits

Ce projet suit la convention [Conventional Commits](https://www.conventionalcommits.org/) :

- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `chore:` configuration, maintenance
- `docs:` documentation
- `test:` ajout ou modification de tests
- `refactor:` réorganisation de code sans changement de comportement
- `ci:` modification du pipeline d'intégration continue

### Versionnage

Ce projet suit le [versionnage sémantique](https://semver.org/) (`vMAJOR.MINOR.PATCH`),
avec un tag posé à la fin de chaque étape majeure (`v0.1.0` à `v0.5.0` à date).

### Gestion des environnements et secrets

3 environnements GitHub distincts (`development`, `test`, `production`) isolent
la configuration selon le contexte d'exécution. Deux niveaux de secrets :
- **Local** : fichier `.env` (non versionné), gabarit `.env.example` (versionné).
- **CI/CD** : GitHub Secrets, injectés comme variables d'environnement au
  moment de l'exécution du pipeline (le service PostgreSQL de test en CI utilise
  des identifiants temporaires sans conséquence, propres au conteneur éphémère).

## Documentation complémentaire

- [`docs/schema_UML_BDD.md`](docs/schema_UML_BDD.md) — schéma de la base de données et raisonnement de conception
- [`docs/model_card.md`](docs/model_card.md) — fiche technique du modèle de Machine Learning (performances, limites, maintenance)
- Documentation interactive de l'API : `/docs` (Swagger) une fois l'API lancée

## Limites connues et améliorations possibles

Les choix suivants ont été faits consciemment pour ce périmètre de POC, avec
leur justification :

| Sujet | Choix actuel | Amélioration possible |
|---|---|---|
| **Migrations de schéma** | `Base.metadata.create_all()` (ne modifie jamais une table existante) | [Alembic](https://alembic.sqlalchemy.org/), pour gérer l'évolution du schéma en production sans perte de données |
| **Distribution du modèle** | `models/model_pipeline.joblib` (90 Ko) committé directement dans Git | Git LFS ou stockage externe (S3, Hugging Face Hub Models) si le modèle devenait volumineux |
| **Dépendance `imbalanced-learn`** | Placée en dépendance de production, car nécessaire pour désérialiser le pipeline entraîné (qui référence `SMOTETomek` utilisé à l'entraînement) | Ré-exporter un pipeline scikit-learn pur sans dépendance résiduelle à `imblearn` |
| **Base de données en production** | Interaction avec PostgreSQL prévue **uniquement en local** (conforme à l'énoncé) : `/predict` renvoie une erreur 500 explicite une fois déployé sur Render, faute de base accessible | Base PostgreSQL managée (ex: Render Postgres) pour une démo entièrement fonctionnelle en ligne |
| **Authentification API** | Aucune (POC) | Clé d'API ou OAuth2 avant toute exposition publique réelle |

## Auteur

Cheun Pelleter - Formation Data Scientist, OpenClassrooms