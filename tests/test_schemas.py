"""Tests unitaires des schémas Pydantic (api/schemas.py)."""
import pytest
from pydantic import ValidationError

from api.schemas import EmployePredictionInput, PredictionRequest


EMPLOYE_VALIDE = EmployePredictionInput.model_config["json_schema_extra"]["example"]


def test_employe_valide_est_accepte():
    """Le jeu de données d'exemple (utilisé dans la doc Swagger) doit
    toujours être valide — sinon la documentation elle-même serait fausse."""
    employe = EmployePredictionInput(**EMPLOYE_VALIDE)
    assert employe.genre == "F"
    assert employe.age == 34


def test_genre_invalide_est_rejete():
    """Une valeur hors de la liste autorisée pour un champ Literal doit
    être rejetée avec une ValidationError explicite."""
    donnees = EMPLOYE_VALIDE.copy()
    donnees["genre"] = "Autre"  # valeur non prévue

    with pytest.raises(ValidationError):
        EmployePredictionInput(**donnees)


def test_age_negatif_est_rejete():
    """Un âge négatif n'a aucun sens métier, doit être rejeté par la
    contrainte Field(gt=0)."""
    donnees = EMPLOYE_VALIDE.copy()
    donnees["age"] = -5

    with pytest.raises(ValidationError):
        EmployePredictionInput(**donnees)


def test_age_superieur_100_est_rejete():
    """Contrainte symétrique à la précédente : borne haute de l'âge."""
    donnees = EMPLOYE_VALIDE.copy()
    donnees["age"] = 150

    with pytest.raises(ValidationError):
        EmployePredictionInput(**donnees)


def test_satisfaction_hors_echelle_est_rejetee():
    """Les scores de satisfaction sont sur une échelle 1-4 (vérifiée via
    .describe() sur les données d'entraînement) - une valeur de 10 n'existe
    pas dans les données que le modèle a appris et doit être refusée."""
    donnees = EMPLOYE_VALIDE.copy()
    donnees["satisfaction_employee_environnement"] = 10

    with pytest.raises(ValidationError):
        EmployePredictionInput(**donnees)


def test_champ_obligatoire_manquant_est_rejete():
    """Aucun champ n'est optionnel dans ce schéma : en retirer un
    quelconque doit provoquer un rejet, pas une valeur par défaut silencieuse."""
    donnees = EMPLOYE_VALIDE.copy()
    del donnees["burnout_score"]

    with pytest.raises(ValidationError):
        EmployePredictionInput(**donnees)


def test_prediction_request_englobe_matricule_et_employe():
    """Vérifie que l'enveloppe PredictionRequest fonctionne correctement
    avec un matricule et des données employé valides imbriquées."""
    request = PredictionRequest(matricule="4521", employe=EMPLOYE_VALIDE)
    assert request.matricule == "4521"
    assert request.employe.genre == "F"