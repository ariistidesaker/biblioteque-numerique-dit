"""
train.py — Étape 2 du pipeline DVC
Entraîne un modèle de recommandation basé sur le filtrage collaboratif
par similarité cosinus (User-Based Collaborative Filtering).

Usage :
    python -m app.ml.train \
        --input  data/processed_loans.csv \
        --output models/model.pkl
"""

import argparse
import logging
import os
import pickle

import numpy as np
import pandas as pd
from .model import UserBasedRecommender

logging.basicConfig(level=logging.INFO, format="%(asctime)s [TRAIN] %(message)s")
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Entraînement du modèle de recommandation.")
    parser.add_argument("--input",       default="data/processed_loans.csv", help="CSV prétraité")
    parser.add_argument("--output",      default="models/model.pkl",         help="Chemin de sauvegarde du modèle")
    parser.add_argument("--n_neighbors", type=int, default=10,               help="Nombre de voisins")
    parser.add_argument("--n_reco",      type=int, default=5,                help="Nombre de recommandations")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        logger.error(f"Fichier introuvable : {args.input}")
        raise FileNotFoundError(args.input)

    df = pd.read_csv(args.input)
    logger.info(f"Données chargées : {len(df)} paires utilisateur-livre.")

    model = UserBasedRecommender(
        n_neighbors=args.n_neighbors,
        n_recommendations=args.n_reco,
    )
    model.fit(df)
    model.save(args.output)
    logger.info("✅ Entraînement terminé.")


if __name__ == "__main__":
    main()
