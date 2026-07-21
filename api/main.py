"""Point d'entrée de l'API FastAPI - Prédiction du risque de départ des employés."""
from fastapi import FastAPI, HTTPException

from api.schemas import PredictionRequest, PredictionOutput
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
def predict_turnover(request: PredictionRequest):
    """Prédit le risque de départ d'un employé à partir de ses données RH.

    `request.matricule` identifie l'employé pour la BDD (table EMPLOYES) et
    n'est jamais envoyé au modèle. `request.employe` contient les 28
    features RH utilisées pour la prédiction elle-même.

    Retourne la probabilité de départ, la prédiction binaire (0/1),
    le label associé, et le seuil de décision utilisé.
    """
    try:
        result = predict(request.employe.model_dump())

        # TODO (Étape 4 - SQLAlchemy) : logique "chercher ou créer"
        # 1. Chercher un employé existant en base via request.matricule
        # 2. S'il existe : mettre à jour ses données avec request.employe
        #    S'il n'existe pas : le créer, PostgreSQL génère son id
        # 3. Insérer une nouvelle ligne dans PREDICTIONS avec :
        #    - employe_id = l'id récupéré/créé à l'étape 2
        #    - donnees_entree = request.employe.model_dump() (instantané JSON)
        #    - probabilite_depart, prediction, label, seuil_utilise = result

        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction : {str(e)}"
        )