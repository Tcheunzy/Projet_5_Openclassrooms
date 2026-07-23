"""Schémas Pydantic pour la validation des données de l'API."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EmployePredictionInput(BaseModel):
    """Données d'un employé nécessaires pour prédire le risque de départ."""

    # --- Champs catégoriels (valeurs strictement limitées) ---
    genre: Literal["F", "M"]
    statut_marital: Literal["Célibataire", "Divorcé(e)", "Marié(e)"]
    poste: Literal[
        "Assistant de Direction", "Cadre Commercial", "Consultant",
        "Directeur Technique", "Manager", "Représentant Commercial",
        "Ressources Humaines", "Senior Manager", "Tech Lead",
    ]
    domaine_etude: Literal[
        "Autre", "Entrepreunariat", "Infra & Cloud",
        "Marketing", "Ressources Humaines", "Transformation Digitale",
    ]
    frequence_deplacement: Literal["Frequent", "Jamais", "Occasionnel"]

    # --- Champs numériques ---
    nb_formations_suivies: int = Field(ge=0)
    niveau_education: int = Field(ge=1, le=5)
    age: int = Field(gt=0, lt=100)
    annee_experience_totale: float = Field(ge=0)
    annees_dans_l_entreprise: float = Field(ge=0)
    satisfaction_employee_environnement: int = Field(ge=1, le=4)
    satisfaction_employee_nature_travail: int = Field(ge=1, le=4)
    satisfaction_employee_equipe: int = Field(ge=1, le=4)
    satisfaction_employee_equilibre_pro_perso: int = Field(ge=1, le=4)
    note_evaluation_actuelle: int = Field(ge=3, le=4)
    heure_supplementaires: Literal[0, 1] = Field(description="0 = Non, 1 = Oui")
    augementation_salaire_precedente: float = Field(description="En %")
    burnout_score: float
    contrainte_mobilite: Literal[0, 1] = Field(description="0 = Non, 1 = Oui")
    ratio_stagnation_promotion: float
    augmentation_vs_perf: float
    revenu_par_annee_experience: float = Field(ge=0)
    score_satisfaction_global: float
    delta_evaluation: float
    ratio_experience_entreprises: float
    instabilite_carriere: float
    engagement_formation: float
    epargne_d_entreprise: float = Field(ge=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nb_formations_suivies": 2,
                "niveau_education": 3,
                "age": 34,
                "annee_experience_totale": 8,
                "annees_dans_l_entreprise": 3,
                "satisfaction_employee_environnement": 3,
                "satisfaction_employee_nature_travail": 2,
                "satisfaction_employee_equipe": 3,
                "satisfaction_employee_equilibre_pro_perso": 2,
                "note_evaluation_actuelle": 3,
                "heure_supplementaires": 1,
                "augementation_salaire_precedente": 12,
                "burnout_score": 0.6,
                "contrainte_mobilite": 0,
                "ratio_stagnation_promotion": 0.3,
                "augmentation_vs_perf": 1.1,
                "revenu_par_annee_experience": 450,
                "score_satisfaction_global": 2.5,
                "delta_evaluation": -0.2,
                "ratio_experience_entreprises": 0.4,
                "instabilite_carriere": 0.2,
                "engagement_formation": 0.5,
                "epargne_d_entreprise": 1,
                "frequence_deplacement": "Frequent",
                "domaine_etude": "Marketing",
                "genre": "F",
                "statut_marital": "Célibataire",
                "poste": "Cadre Commercial",
            }
        }
    )


class PredictionRequest(BaseModel):
    """Enveloppe de la requête de prédiction : identifie l'employé (matricule,
    utilisé pour le lien vers la table EMPLOYES en base) en plus de ses
    données RH (utilisées, elles, pour la prédiction elle-même)."""

    matricule: str = Field(description="Identifiant métier de l'employé chez Futurisys")
    employe: EmployePredictionInput

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "matricule": "4521",
                "employe": EmployePredictionInput.model_config["json_schema_extra"]["example"],
            }
        }
    )


class PredictionOutput(BaseModel):
    """Résultat renvoyé par l'API après prédiction."""

    probabilite_depart: float = Field(ge=0, le=1)
    prediction: Literal[0, 1]
    label: str
    seuil_utilise: float