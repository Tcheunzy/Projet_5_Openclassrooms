"""Tests unitaires du module de prédiction (src/predict.py)."""
import pytest

from src.predict import predict, _metadata


# Un jeu de données valide et complet, réutilisé comme base dans plusieurs tests
EMPLOYE_VALIDE = {
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


def test_metadata_contient_28_colonnes():
    """Vérifie que le fichier de métadonnées correspond au nombre de
    features attendu par le modèle entraîné."""
    assert len(_metadata["all_input_columns"]) == 28


def test_predict_retourne_les_bonnes_cles():
    """Une prédiction valide doit renvoyer exactement les 4 clés attendues."""
    result = predict(EMPLOYE_VALIDE)
    assert set(result.keys()) == {
        "probabilite_depart", "prediction", "label", "seuil_utilise"
    }


def test_predict_probabilite_dans_intervalle_0_1():
    """La probabilité renvoyée doit toujours être une probabilité valide."""
    result = predict(EMPLOYE_VALIDE)
    assert 0.0 <= result["probabilite_depart"] <= 1.0


def test_predict_seuil_utilise_est_correct():
    """Le seuil renvoyé doit correspondre à celui défini dans les métadonnées
    du modèle (0.40), pas une valeur arbitraire codée en dur ailleurs."""
    result = predict(EMPLOYE_VALIDE)
    assert result["seuil_utilise"] == _metadata["threshold"]


def test_predict_coherence_prediction_et_label():
    """La prédiction binaire (0/1) doit toujours correspondre au bon label texte."""
    result = predict(EMPLOYE_VALIDE)
    if result["prediction"] == 1:
        assert result["label"] == "Démission"
    else:
        assert result["label"] == "En poste"


def test_predict_coherence_prediction_et_seuil():
    """La prédiction doit être cohérente avec la comparaison probabilité/seuil :
    c'est la règle métier fondamentale que predict() est censé appliquer."""
    result = predict(EMPLOYE_VALIDE)
    seuil = result["seuil_utilise"]
    proba = result["probabilite_depart"]
    prediction_attendue = int(proba >= seuil)
    assert result["prediction"] == prediction_attendue


def test_predict_leve_erreur_si_colonne_manquante():
    """Si une feature obligatoire manque, predict() doit lever une ValueError
    explicite plutôt que de produire un résultat silencieusement faux
    (ex: imputation automatique d'une valeur jamais fournie par le client)."""
    employe_incomplet = EMPLOYE_VALIDE.copy()
    del employe_incomplet["age"]

    with pytest.raises(ValueError, match="age"):
        predict(employe_incomplet)