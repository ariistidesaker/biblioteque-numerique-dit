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
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO, format="%(asctime)s [TRAIN] %(message)s")
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# Modèle : User-Based Collaborative Filtering
# ─────────────────────────────────────────────────────────────────

class UserBasedRecommender:
    """
    Recommandeur basé sur la similarité cosinus entre utilisateurs.

    L'idée : pour un utilisateur cible, trouver les N utilisateurs
    les plus similaires (en termes d'historique d'emprunts), puis
    recommander les livres que ces voisins ont beaucoup appréciés
    mais que l'utilisateur cible n'a pas encore lu.
    """

    def __init__(self, n_neighbors: int = 10, n_recommendations: int = 5):
        self.n_neighbors = n_neighbors
        self.n_recommendations = n_recommendations
        # Remplis lors du fit()
        self.user_item_matrix: pd.DataFrame | None = None
        self.similarity_matrix: np.ndarray | None = None
        self.user_index: dict = {}       # user_id -> row index
        self.item_index: dict = {}       # livre_id -> col index
        self.reverse_item_index: dict = {}  # col index -> livre_id

    # ── Entraînement ──────────────────────────────────────────────

    def fit(self, df: pd.DataFrame) -> "UserBasedRecommender":
        """
        Construit la matrice utilisateur-item et calcule la matrice
        de similarité cosinus entre tous les utilisateurs.

        Args:
            df: DataFrame avec colonnes ['utilisateur_id', 'livre_id', 'score']
        """
        logger.info("Construction de la matrice utilisateur-item…")

        # Pivot : lignes = utilisateurs, colonnes = livres
        matrix = df.pivot_table(
            index="utilisateur_id",
            columns="livre_id",
            values="score",
            aggfunc="max",
            fill_value=0.0
        )
        self.user_item_matrix = matrix
        self.user_index = {uid: i for i, uid in enumerate(matrix.index)}
        self.item_index = {iid: j for j, iid in enumerate(matrix.columns)}
        self.reverse_item_index = {j: iid for iid, j in self.item_index.items()}

        logger.info(
            f"  → Matrice : {matrix.shape[0]} utilisateurs × {matrix.shape[1]} livres"
        )

        # Similarité cosinus entre utilisateurs
        logger.info("Calcul de la matrice de similarité cosinus…")
        values = matrix.values.astype(float)
        self.similarity_matrix = cosine_similarity(values)
        logger.info("  → Similarité calculée.")

        return self

    # ── Prédiction ────────────────────────────────────────────────

    def recommend(self, user_id: str, n: int | None = None) -> list[int]:
        """
        Retourne les IDs de livres recommandés pour `user_id`.

        Args:
            user_id : identifiant de l'utilisateur (UUID string)
            n       : nombre de recommandations (défaut = self.n_recommendations)

        Returns:
            Liste d'IDs de livres triés par score estimé décroissant.
            Si l'utilisateur est inconnu, retourne les livres les plus populaires.
        """
        n = n or self.n_recommendations

        if user_id not in self.user_index:
            logger.info(f"Utilisateur inconnu '{user_id}' → fallback popularité")
            return self._popular_books(n)

        user_idx = self.user_index[user_id]
        sim_scores = self.similarity_matrix[user_idx]

        # Top K voisins (sans compter l'utilisateur lui-même)
        neighbor_indices = np.argsort(sim_scores)[::-1]
        neighbor_indices = [i for i in neighbor_indices if i != user_idx][:self.n_neighbors]

        # Livres déjà empruntés par l'utilisateur cible
        user_row = self.user_item_matrix.values[user_idx]
        already_read = set(np.where(user_row > 0)[0])

        # Score pondéré pour chaque livre candidat
        scores = np.zeros(self.user_item_matrix.shape[1])
        sim_sum = np.zeros(self.user_item_matrix.shape[1])

        for neighbor_idx in neighbor_indices:
            sim = sim_scores[neighbor_idx]
            neighbor_row = self.user_item_matrix.values[neighbor_idx]
            scores += sim * neighbor_row
            sim_sum += np.where(neighbor_row > 0, sim, 0)

        # Normalisation (éviter division par zéro)
        with np.errstate(divide="ignore", invalid="ignore"):
            normalized = np.where(sim_sum > 0, scores / sim_sum, 0)

        # Exclure les livres déjà lus
        for idx in already_read:
            normalized[idx] = 0.0

        # Top N
        top_indices = np.argsort(normalized)[::-1][:n]
        top_indices = [i for i in top_indices if normalized[i] > 0]

        # Fallback si pas assez de résultats
        if len(top_indices) < n:
            popular = self._popular_books(n, exclude=already_read)
            seen_ids = {self.reverse_item_index[i] for i in top_indices}
            extras = [bid for bid in popular if bid not in seen_ids]
            result_ids = [self.reverse_item_index[i] for i in top_indices]
            result_ids += extras[: n - len(result_ids)]
            return result_ids

        return [self.reverse_item_index[i] for i in top_indices]

    def _popular_books(self, n: int, exclude: set = None) -> list[int]:
        """Retourne les livres les plus empruntés (par score agrégé)."""
        if self.user_item_matrix is None:
            return []
        exclude = exclude or set()
        popularity = self.user_item_matrix.values.sum(axis=0)
        sorted_indices = np.argsort(popularity)[::-1]
        result = []
        for idx in sorted_indices:
            if idx not in exclude:
                result.append(self.reverse_item_index[idx])
            if len(result) >= n:
                break
        return result

    # ── Sérialisation ─────────────────────────────────────────────

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)
        logger.info(f"Modèle sauvegardé → {path}")

    @classmethod
    def load(cls, path: str) -> "UserBasedRecommender":
        with open(path, "rb") as f:
            model = pickle.load(f)
        logger.info(f"Modèle chargé depuis → {path}")
        return model


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
