"""Configuration de la connexion à la base de données PostgreSQL."""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()  # charge les variables du fichier .env dans l'environnement du processus

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/projet5")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Fournit une session de base de données, et la ferme systématiquement après usage."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()