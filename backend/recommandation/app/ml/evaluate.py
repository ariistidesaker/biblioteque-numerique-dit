"""
evaluate.py — Étape 3 du pipeline DVC
Évalue la qualité du modèle de recommandation entraîné.

Métriques calculées :
- Couverture    : % des livres du catalogue qui apparaissent dans au moins une recommandation
- Précision@K   : parmi les K recommandations, combien correspondent à de vraies interactions ?
                  (évaluée sur un ensemble de test hold-out)
- Recall@K      : proportion des interactions réelles retrouvées dans les K recommandations

Usage :
    python -m app.ml.evaluate \
        --data    data/processed_loans.csv \
        --model   models/model.pkl \
        --metrics models/metrics.json
"""

import argparse
import json
import logging
import os
import random

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [EVAL] %(message)s")
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────

def train_test_split_interactions(df: pd.DataFrame, test_ratio: float = 0.2, seed: int = 42):
    """
    Divise les interactions par utilisateur :
    - Pour chaque utilisateur, garde (1 - test_ratio) de ses interactions pour l'entraînement.
    - Le reste constitue l'ensemble de test.
    """
    rng = random.Random(seed)
    train_rows, test_rows = [], []

    for user_id, group in df.groupby("utilisateur_id"):
        rows = group.to_dict("records")
        rng.shuffle(rows)
        cut = max(1, int(len(rows) * (1 - test_ratio)))
        train_rows.extend(rows[:cut])
        test_rows.extend(rows[cut:])

    return pd.DataFrame(train_rows), pd.DataFrame(test_rows)


def precision_at_k(recommended: list, relevant: set, k: int) -> float:
    """Précision@K : proportion de recommandations pertinentes parmi les K premières."""
    top_k = recommended[:k]
    hits = sum(1 for item in top_k if item in relevant)
    return hits / k if k > 0 else 0.0


def recall_at_k(recommended: list, relevant: set, k: int) -> float:
    """Recall@K : proportion d'items pertinents retrouvés parmi les K recommandations."""
    top_k = recommended[:k]
    hits = sum(1 for item in top_k if item in relevant)
    return hits / len(relevant) if relevant else 0.0


def catalog_coverage(all_recommendations: list[list], n_total_books: int) -> float:
    """Couverture du catalogue : % de livres qui apparaissent dans au moins une recommandation."""
    recommended_books = set()
    for recs in all_recommendations:
        recommended_books.update(recs)
    return len(recommended_books) / n_total_books if n_total_books > 0 else 0.0


# ─────────────────────────────────────────────────────────────────
# Évaluation principale
# ─────────────────────────────────────────────────────────────────

def evaluate(model, df: pd.DataFrame, k: int = 5) -> dict:
    """
    Évalue le modèle en mode hold-out :
    1. Split train/test
    2. Ré-entraîne le modèle sur train
    3. Mesure Précision@K, Recall@K et Couverture sur test

    Retourne un dictionnaire de métriques.
    """
    logger.info(f"Évaluation du modèle (K={k})…")

    # Filtrer les utilisateurs avec au moins 2 interactions (sinon pas de split possible)
    user_counts = df.groupby("utilisateur_id").size()
    valid_users = user_counts[user_counts >= 2].index
    df_eval = df[df["utilisateur_id"].isin(valid_users)]

    if df_eval.empty:
        logger.warning("Pas assez d'interactions pour évaluer. Métriques = 0.")
        return {"precision_at_k": 0.0, "recall_at_k": 0.0, "coverage": 0.0, "k": k, "n_users_evaluated": 0}

    df_train, df_test = train_test_split_interactions(df_eval, test_ratio=0.2)

    # Ré-entraîner sur le sous-ensemble train
    model.fit(df_train)

    # Ensemble de test : livres réels par utilisateur
    test_items_by_user: dict[str, set] = {}
    for row in df_test.to_dict("records"):
        uid = row["utilisateur_id"]
        test_items_by_user.setdefault(uid, set()).add(row["livre_id"])

    precision_scores, recall_scores = [], []
    all_recs = []
    n_total_books = df["livre_id"].nunique()

    for user_id, relevant_items in test_items_by_user.items():
        recs = model.recommend(user_id, n=k)
        all_recs.append(recs)
        precision_scores.append(precision_at_k(recs, relevant_items, k))
        recall_scores.append(recall_at_k(recs, relevant_items, k))

    metrics = {
        "precision_at_k": round(float(np.mean(precision_scores)), 4),
        "recall_at_k":    round(float(np.mean(recall_scores)), 4),
        "coverage":       round(catalog_coverage(all_recs, n_total_books), 4),
        "k":              k,
        "n_users_evaluated": len(test_items_by_user),
    }

    logger.info(
        f"  Précision@{k} = {metrics['precision_at_k']:.4f} | "
        f"Recall@{k} = {metrics['recall_at_k']:.4f} | "
        f"Couverture = {metrics['coverage']:.4f} | "
        f"Utilisateurs évalués = {metrics['n_users_evaluated']}"
    )
    return metrics


# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Évaluation du modèle de recommandation.")
    parser.add_argument("--data",    default="data/processed_loans.csv", help="CSV prétraité")
    parser.add_argument("--model",   default="models/model.pkl",         help="Modèle .pkl entraîné")
    parser.add_argument("--metrics", default="models/metrics.json",      help="Fichier de sortie des métriques")
    parser.add_argument("--k",       type=int, default=5,                help="K pour Précision@K et Recall@K")
    args = parser.parse_args()

    # Chargement du modèle
    if not os.path.exists(args.model):
        logger.error(f"Modèle introuvable : {args.model}")
        raise FileNotFoundError(args.model)

    # Import local pour éviter les imports circulaires
    from app.ml.train import UserBasedRecommender
    model = UserBasedRecommender.load(args.model)

    # Chargement des données
    if not os.path.exists(args.data):
        logger.error(f"Données introuvables : {args.data}")
        raise FileNotFoundError(args.data)

    df = pd.read_csv(args.data)
    logger.info(f"Données chargées : {len(df)} interactions.")

    metrics = evaluate(model, df, k=args.k)

    # Sauvegarde des métriques
    os.makedirs(os.path.dirname(args.metrics) if os.path.dirname(args.metrics) else ".", exist_ok=True)
    with open(args.metrics, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    logger.info(f"Métriques sauvegardées → {args.metrics}")
    logger.info("✅ Évaluation terminée.")


if __name__ == "__main__":
    main()
