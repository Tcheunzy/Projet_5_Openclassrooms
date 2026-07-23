"""Fixtures partagées pour l'ensemble de la suite de tests."""
import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from database.connection import Base, get_db
from database.models_db import Employe, Prediction  # noqa: F401

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


@pytest.fixture(scope="session")
def db_engine():
    """Crée toutes les tables une fois pour toute la session de tests,
    et les détruit à la fin — la base de test démarre et termine vide."""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine):
    """Fournit une session isolée par test : chaque test s'exécute dans une
    transaction qui est annulée (rollback) à la fin, pour qu'un test n'ait
    jamais d'effet sur les suivants, même en cas d'échec en cours de route."""
    connection = db_engine.connect()
    transaction = connection.begin()
    SessionTest = sessionmaker(bind=connection)
    session = SessionTest()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Client de test FastAPI, avec la dépendance get_db remplacée par
    notre session de test isolée plutôt que la vraie base projet5."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()