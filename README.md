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
- Mettre en place un pipeline CI/CD (GitHub Actions + Hugging Face Spaces)
- Documenter l'ensemble du projet pour en assurer la maintenabilité

## Architecture du projet

\```
├── api/            # API FastAPI (endpoints, schémas Pydantic)
├── data/           # Données brutes et traitées (non versionnées)
├── database/       # Scripts de création et gestion de la base PostgreSQL
├── docs/           # Documentation technique complémentaire
├── models/         # Modèles de ML entraînés (non versionnés)
├── notebooks/      # Notebooks d'exploration et d'entraînement
├── src/            # Code source réutilisable (preprocessing, prédiction)
├── tests/          # Tests unitaires et fonctionnels (Pytest)
└── .github/        # Pipelines CI/CD (GitHub Actions)
\```

## Installation

### Prérequis
- Python 3.12
- [uv](https://docs.astral.sh/uv/) (gestionnaire de paquets Python)
- PostgreSQL (installation locale)

### Étapes

1. Cloner le dépôt
\```bash
git clone https://github.com/Tcheunzy/Projet_5_Openclassrooms.git
cd Projet_5_Openclassrooms
\```

2. Installer les dépendances
\```bash
uv sync
\```

3. Configurer les variables d'environnement
\```bash
cp .env.example .env
# Renseigner les valeurs dans .env
\```

## Utilisation

*(à compléter à l'Étape 3 - lancement de l'API)*

## Base de données

*(à compléter à l'Étape 4)*

## Tests

*(à compléter à l'Étape 5)*

## Déploiement

*(à compléter à l'Étape 2)*

## Auteur

Cheun Pelleter - Formation Data Scientist, OpenClassrooms