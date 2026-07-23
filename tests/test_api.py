"""Tests fonctionnels des endpoints FastAPI (nécessitent une vraie base de
test PostgreSQL, gérée par les fixtures de conftest.py)."""
from api.schemas import EmployePredictionInput
from database.models_db import Employe, Prediction

EMPLOYE_VALIDE = EmployePredictionInput.model_config["json_schema_extra"]["example"]


def test_root_renvoie_200(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_health_renvoie_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_predict_nouvel_employe_renvoie_200(client):
    """Un appel valide doit renvoyer une prédiction structurée correctement."""
    payload = {"matricule": "TEST001", "employe": EMPLOYE_VALIDE}
    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {
        "probabilite_depart", "prediction", "label", "seuil_utilise"
    }
    assert 0.0 <= body["probabilite_depart"] <= 1.0


def test_predict_nouvel_employe_est_persiste_en_base(client, db_session):
    """Vérifie que l'appel crée bien une ligne EMPLOYES et une ligne
    PREDICTIONS liées entre elles - le coeur de l'Étape 4."""
    payload = {"matricule": "TEST002", "employe": EMPLOYE_VALIDE}
    client.post("/predict", json=payload)

    employe_db = db_session.query(Employe).filter_by(matricule="TEST002").first()
    assert employe_db is not None
    assert employe_db.genre == "F"

    predictions = db_session.query(Prediction).filter_by(employe_id=employe_db.id).all()
    assert len(predictions) == 1
    assert predictions[0].donnees_entree["age"] == 34


def test_predict_matricule_existant_met_a_jour_sans_dupliquer(client, db_session):
    """Deux appels avec le même matricule doivent : mettre à jour l'employé
    (pas créer de doublon), et accumuler 2 lignes dans PREDICTIONS avec
    des instantanés différents - le comportement validé manuellement à
    l'Étape 4, maintenant automatisé."""
    payload_1 = {"matricule": "TEST003", "employe": {**EMPLOYE_VALIDE, "age": 34}}
    payload_2 = {"matricule": "TEST003", "employe": {**EMPLOYE_VALIDE, "age": 40}}

    client.post("/predict", json=payload_1)
    client.post("/predict", json=payload_2)

    employes = db_session.query(Employe).filter_by(matricule="TEST003").all()
    assert len(employes) == 1
    assert employes[0].age == 40  # dernière valeur envoyée

    predictions = (
        db_session.query(Prediction)
        .filter_by(employe_id=employes[0].id)
        .order_by(Prediction.id)
        .all()
    )
    assert len(predictions) == 2
    assert predictions[0].donnees_entree["age"] == 34  # instantané figé du 1er appel
    assert predictions[1].donnees_entree["age"] == 40  # instantané figé du 2nd appel


def test_predict_donnees_invalides_renvoie_422(client):
    """Une valeur catégorielle hors énumération doit être rejetée avant
    même d'atteindre la logique métier ou la base de données."""
    donnees_invalides = {**EMPLOYE_VALIDE, "genre": "Autre"}
    payload = {"matricule": "TEST004", "employe": donnees_invalides}

    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_matricule_manquant_renvoie_422(client):
    """PredictionRequest exige un matricule - un payload qui ne contient
    que les données employé (ancien format d'avant l'Étape 4) doit être
    rejeté, pas silencieusement accepté avec un matricule vide."""
    payload = {"employe": EMPLOYE_VALIDE}  # matricule absent

    response = client.post("/predict", json=payload)
    assert response.status_code == 422

def test_predict_erreur_interne_renvoie_500(client, monkeypatch):
    """Si predict() lève une exception inattendue (ex: modèle corrompu,
    bug interne), l'API doit répondre 500 avec un message clair, plutôt
    que de laisser planter le serveur ou renvoyer une erreur opaque."""

    def predict_qui_plante(_):
        raise RuntimeError("Erreur simulée pour le test")

    monkeypatch.setattr("api.main.predict", predict_qui_plante)

    payload = {"matricule": "TEST005", "employe": EMPLOYE_VALIDE}
    response = client.post("/predict", json=payload)

    assert response.status_code == 500
    assert "Erreur simulée pour le test" in response.json()["detail"]