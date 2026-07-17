"""Module de chargement du modèle et de prédiction.

Isolé de la couche API pour rester réutilisable indépendamment de FastAPI.
"""
import json
from pathlib import Path

import joblib
import pandas as pd

MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
MODEL_PATH = MODEL_DIR / "model_pipeline.joblib"
METADATA_PATH = MODEL_DIR / "model_metadata.json"


def load_metadata() -> dict:
    """Charge les métadonnées du modèle (colonnes attendues, seuil, labels)."""
    with open(METADATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_model():
    """Charge le pipeline scikit-learn entraîné (preprocessing + modèle)."""
    return joblib.load(MODEL_PATH)


_model = load_model()
_metadata = load_metadata()


def predict(input_data: dict) -> dict:
    """Réalise une prédiction de départ d'employé.

    Args:
        input_data: dictionnaire avec les 27 features attendues par le modèle.

    Returns:
        dict avec la probabilité, la prédiction binaire et le label associé.
    """
    df = pd.DataFrame([input_data], columns=_metadata["all_input_columns"])

    proba = _model.predict_proba(df)[0, 1]
    threshold = _metadata["threshold"]
    prediction = int(proba >= threshold)

    return {
        "probabilite_depart": round(float(proba), 4),
        "prediction": prediction,
        "label": _metadata["target_labels"][str(prediction)],
        "seuil_utilise": threshold,
    }
