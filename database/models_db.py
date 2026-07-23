"""Modèles SQLAlchemy — traduction du schéma UML en tables PostgreSQL."""
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Float, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from database.connection import Base


class Employe(Base):
    """État courant des données RH d'un employé (une ligne = un employé)."""

    __tablename__ = "employes"

    id = Column(Integer, primary_key=True, index=True)
    matricule = Column(String, unique=True, nullable=False, index=True)

    genre = Column(String, nullable=False)
    statut_marital = Column(String, nullable=False)
    poste = Column(String, nullable=False)
    domaine_etude = Column(String, nullable=False)
    frequence_deplacement = Column(String, nullable=False)

    niveau_education = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)
    nb_formations_suivies = Column(Integer, nullable=False)
    annee_experience_totale = Column(Float, nullable=False)
    annees_dans_l_entreprise = Column(Float, nullable=False)
    satisfaction_employee_environnement = Column(Integer, nullable=False)
    satisfaction_employee_nature_travail = Column(Integer, nullable=False)
    satisfaction_employee_equipe = Column(Integer, nullable=False)
    satisfaction_employee_equilibre_pro_perso = Column(Integer, nullable=False)
    note_evaluation_actuelle = Column(Integer, nullable=False)
    heure_supplementaires = Column(Integer, nullable=False)
    augementation_salaire_precedente = Column(Float, nullable=False)
    burnout_score = Column(Float, nullable=False)
    contrainte_mobilite = Column(Integer, nullable=False)
    ratio_stagnation_promotion = Column(Float, nullable=False)
    augmentation_vs_perf = Column(Float, nullable=False)
    revenu_par_annee_experience = Column(Float, nullable=False)
    score_satisfaction_global = Column(Float, nullable=False)
    delta_evaluation = Column(Float, nullable=False)
    ratio_experience_entreprises = Column(Float, nullable=False)
    instabilite_carriere = Column(Float, nullable=False)
    engagement_formation = Column(Float, nullable=False)
    epargne_d_entreprise = Column(Float, nullable=False)

    date_maj = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    predictions = relationship("Prediction", back_populates="employe")


class Prediction(Base):
    """Historique de chaque interaction avec le modèle (une ligne = une prédiction)."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey("employes.id"), nullable=False)

    date_prediction = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc), nullable=False)
    donnees_entree = Column(JSONB, nullable=False)

    probabilite_depart = Column(Float, nullable=False)
    prediction = Column(Integer, nullable=False)
    label = Column(String, nullable=False)
    seuil_utilise = Column(Float, nullable=False)

    employe = relationship("Employe", back_populates="predictions")