"""Point d'entrée de l'API FastAPI - Prédiction du risque de départ des employés."""
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from api.schemas import PredictionRequest, PredictionOutput
from database.connection import get_db
from database.models_db import Employe, Prediction
from src.predict import predict

app = FastAPI(
    title="Futurisys - API de prédiction du turnover",
    description="Expose le modèle de Machine Learning (LogisticRegression) "
                 "développé lors du Projet 4, prédisant le risque de départ "
                 "volontaire d'un employé.",
    version="0.2.0",
)


@app.get("/", tags=["Monitoring"])
def root():
    """Endpoint racine - confirme que l'API est en ligne."""
    return {"message": "API Futurisys - Prédiction du turnover", "status": "online"}


@app.get("/health", tags=["Monitoring"])
def health_check():
    """Healthcheck explicite, utilisé par les plateformes de déploiement."""
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictionOutput, tags=["Prédiction"])
def predict_turnover(request: PredictionRequest, db: Session = Depends(get_db)):
    """Prédit le risque de départ d'un employé, et enregistre l'échange en base.

    request.matricule identifie l'employé pour la BDD (table EMPLOYES) et
    n'est jamais envoyé au modèle. request.employe contient les 28 features
    RH utilisées pour la prédiction elle-même.
    """
    try:
        # 1. Prédiction (logique métier, indépendante de la BDD)
        result = predict(request.employe.model_dump())

        # 2. Chercher l'employé existant via son matricule
        employe_db = (
            db.query(Employe)
            .filter(Employe.matricule == request.matricule)
            .first()
        )

        if employe_db is None:
            # 3a. Création d'un nouvel employé
            employe_db = Employe(
                matricule=request.matricule,
                **request.employe.model_dump(),
            )
            db.add(employe_db)
        else:
            # 3b. Mise à jour d'un employé existant
            for champ, valeur in request.employe.model_dump().items():
                setattr(employe_db, champ, valeur)

        # 4. Flush pour obtenir employe_db.id, sans encore commit définitivement
        db.flush()

        # 5. Création de la ligne PREDICTIONS, liée à cet employé
        prediction_db = Prediction(
            employe_id=employe_db.id,
            donnees_entree=request.employe.model_dump(),
            probabilite_depart=result["probabilite_depart"],
            prediction=result["prediction"],
            label=result["label"],
            seuil_utilise=result["seuil_utilise"],
        )
        db.add(prediction_db)

        # 6. Validation définitive des deux opérations ensemble (transaction atomique)
        db.commit()

        return result

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction : {str(e)}"
        )