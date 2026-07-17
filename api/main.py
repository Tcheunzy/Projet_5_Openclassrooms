"""Point d'entrée de l'API FastAPI - Prédiction du risque de départ des employés."""
from fastapi import FastAPI, HTTPException

from api.schemas import EmployePredictionInput, PredictionOutput
from src.predict import predict

app = FastAPI(
    title="Futurisys - API de prédiction du turnover",
    description="Expose le modèle de Machine Learning (LogisticRegression) "
                 "développé lors du Projet 4, prédisant le risque de départ "
                 "volontaire d'un employé.",
    version="0.1.0",
)


@app.get("/", tags=["Monitoring"])
def root():
    """Endpoint racine - confirme que l'API est en ligne."""
    return {"message": "API Futurisys - Prédiction du turnover", "status": "online"}


@app.get("/health", tags=["Monitoring"])
def health_check():
    """Healthcheck explicite, utilisé par les plateformes de déploiement
    (ex: Render) pour vérifier que le service répond correctement."""
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictionOutput, tags=["Prédiction"])
def predict_turnover(employe: EmployePredictionInput):
    """Prédit le risque de départ d'un employé à partir de ses données RH.

    Retourne la probabilité de départ, la prédiction binaire (0/1),
    le label associé, et le seuil de décision utilisé.
    """
    try:
        result = predict(employe.model_dump())
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction : {str(e)}"
        )