"""
model_loader.py — Chargement paresseux (lazy) du modèle ML.

Le modèle est chargé une seule fois au démarrage de l'API.
Si le fichier n'existe pas encore (premier démarrage), le service
démarre quand même et renvoie des recommandations de secours.
"""

import logging
import os
import pickle
from typing import Optional

logger = logging.getLogger(__name__)

# Chemin vers le fichier modèle (configurable via variable d'env)
MODEL_PATH = os.getenv("MODEL_PATH", "/app/model/model.pkl")

# Instance partagée du modèle
_model = None


def load_model():
    """Charge le modèle depuis MODEL_PATH. Retourne None si introuvable."""
    global _model
    if not os.path.exists(MODEL_PATH):
        logger.warning(
            f"Modèle introuvable à '{MODEL_PATH}'. "
            "Le service démarre sans modèle — les recommandations retourneront des livres populaires."
        )
        _model = None
        return None
    try:
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
        logger.info(f"✅ Modèle chargé depuis '{MODEL_PATH}'.")
        return _model
    except Exception as exc:
        logger.error(f"Erreur lors du chargement du modèle : {exc}")
        _model = None
        return None


def get_model():
    """Retourne l'instance courante du modèle (peut être None)."""
    return _model


def reload_model():
    """Force le rechargement du modèle depuis le disque."""
    logger.info("Rechargement du modèle…")
    return load_model()
