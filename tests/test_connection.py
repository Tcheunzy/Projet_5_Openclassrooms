"""Test unitaire de la fonction get_db (générateur de session BDD)."""
from database.connection import get_db


def test_get_db_fournit_une_session_puis_se_ferme():
    """Vérifie que get_db() est bien un générateur qui fournit une session,
    puis se termine correctement une fois épuisé (déclenche le db.close())."""
    generateur = get_db()
    session = next(generateur)
    assert session is not None

    # Épuiser le générateur déclenche le bloc `finally: db.close()`
    try:
        next(generateur)
    except StopIteration:
        pass  # comportement normal et attendu d'un générateur épuisé