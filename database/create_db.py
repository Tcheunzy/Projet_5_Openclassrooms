"""Script de création des tables en base de données.
À lancer une fois pour initialiser la structure : uv run python -m database.create_db"""
from database.connection import engine, Base
from database.models_db import Employe, Prediction  # noqa: F401 — nécessaire pour que Base connaisse ces tables

Base.metadata.create_all(engine)
print("Tables créées avec succès.")