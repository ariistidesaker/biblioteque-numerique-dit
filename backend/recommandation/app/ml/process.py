"""
process.py — Étape 1 du pipeline DVC
Télécharge l'historique d'emprunts depuis le Service Emprunts,
nettoie les données et produit un fichier CSV prêt à l'entraînement.

Usage (via DVC ou en direct) :
    python -m app.ml.process \
        --input  data/raw_loans.csv \
        --output data/processed_loans.csv
"""

import argparse
import os
import sys
import logging

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [PROCESS] %(message)s")
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────

def load_csv(path: str) -> pd.DataFrame:
    """Charge un CSV brut d'emprunts."""
    logger.info(f"Chargement des données brutes depuis : {path}")
    df = pd.read_csv(path)
    logger.info(f"  → {len(df)} lignes chargées.")
    return df


def clean_and_feature_engineer(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoyage et feature engineering :
    - Supprime les lignes avec utilisateur_id ou livre_id manquants
    - Convertit les colonnes de dates
    - Calcule la durée effective d'emprunt (en jours)
    - Crée un score implicite : 1.0 si rendu à temps, 0.5 si rendu en retard, 1.2 si rendu très tôt
    """
    logger.info("Nettoyage et feature engineering…")

    # Colonnes attendues
    required = {"utilisateur_id", "livre_id", "date_emprunt", "date_retour_prevue", "date_retour_effective", "en_retard"}
    missing_cols = required - set(df.columns)
    if missing_cols:
        raise ValueError(f"Colonnes manquantes dans le CSV : {missing_cols}")

    # Suppression des lignes incomplètes
    initial_len = len(df)
    df = df.dropna(subset=["utilisateur_id", "livre_id"])
    logger.info(f"  → {initial_len - len(df)} lignes supprimées (NaN utilisateur/livre).")

    # Conversion de types
    df["livre_id"] = df["livre_id"].astype(int)
    df["en_retard"] = df["en_retard"].astype(bool)

    # Parse des dates
    for col in ["date_emprunt", "date_retour_prevue", "date_retour_effective"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Durée effective (en jours) — NaN si pas encore rendu
    df["duree_jours"] = (df["date_retour_effective"] - df["date_emprunt"]).dt.days

    # Score implicite basé sur le comportement d'emprunt
    # Logique : l'emprunt lui-même = intérêt => score de base 1.0
    # Retard -> pénalité légère (le livre n'était peut-être pas au top)
    # Rendu très tôt (< 3 jours) -> score réduit (peu d'intérêt ?)
    def compute_score(row):
        if pd.isna(row["date_retour_effective"]):
            # Emprunt en cours = intérêt fort
            return 1.0
        days = row["duree_jours"]
        if row["en_retard"]:
            return 0.7  # intérêt mais oubli
        if days is not None and days <= 3:
            return 0.6  # rendu très vite (peu apprécié ?)
        return 1.0  # emprunt normal, rendu dans les temps

    df["score"] = df.apply(compute_score, axis=1)

    # Garder uniquement les colonnes utiles
    result = df[["utilisateur_id", "livre_id", "score"]].copy()

    # En cas d'emprunts multiples du même utilisateur pour le même livre, prendre le max score
    result = (
        result.groupby(["utilisateur_id", "livre_id"], as_index=False)["score"]
        .max()
    )

    logger.info(f"  → {len(result)} paires (utilisateur, livre) après agrégation.")
    return result


def save_csv(df: pd.DataFrame, path: str) -> None:
    """Sauvegarde le DataFrame nettoyé."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    df.to_csv(path, index=False)
    logger.info(f"Données traitées sauvegardées → {path}")


# ─────────────────────────────────────────────────────────────────
# Génération de données synthétiques (fallback si CSV vide/absent)
# ─────────────────────────────────────────────────────────────────

def generate_synthetic_data(n_users: int = 50, n_books: int = 30, n_interactions: int = 300) -> pd.DataFrame:
    """
    Génère des données synthétiques pour permettre l'entraînement
    même si aucun emprunt réel n'a encore été enregistré.
    """
    import numpy as np
    import uuid

    logger.info(f"Génération de données synthétiques ({n_interactions} interactions)…")
    rng = np.random.default_rng(42)

    user_ids = [str(uuid.uuid4()) for _ in range(n_users)]
    book_ids = list(range(1, n_books + 1))

    users = rng.choice(user_ids, size=n_interactions)
    books = rng.choice(book_ids, size=n_interactions)
    scores = rng.choice([0.6, 0.7, 1.0], size=n_interactions, p=[0.15, 0.20, 0.65])

    df = pd.DataFrame({
        "utilisateur_id": users,
        "livre_id": books,
        "score": scores,
    })

    # Agrégation
    df = df.groupby(["utilisateur_id", "livre_id"], as_index=False)["score"].max()
    logger.info(f"  → {len(df)} paires synthétiques générées.")
    return df


# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Étape de prétraitement des données d'emprunts.")
    parser.add_argument("--input",  default="data/raw_loans.csv",       help="Chemin vers le CSV brut d'emprunts")
    parser.add_argument("--output", default="data/processed_loans.csv", help="Chemin de sortie du CSV traité")
    parser.add_argument("--synthetic", action="store_true",             help="Générer des données synthétiques si le CSV est vide")
    args = parser.parse_args()

    # Chargement ou génération
    if os.path.exists(args.input):
        df_raw = load_csv(args.input)
        if df_raw.empty:
            logger.warning("Le CSV brut est vide. Génération de données synthétiques.")
            df_processed = generate_synthetic_data()
        else:
            df_processed = clean_and_feature_engineer(df_raw)
    else:
        logger.warning(f"Fichier introuvable : {args.input}. Génération de données synthétiques.")
        df_processed = generate_synthetic_data()

    save_csv(df_processed, args.output)
    logger.info("✅ Prétraitement terminé.")


if __name__ == "__main__":
    main()
