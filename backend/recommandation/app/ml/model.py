import logging
import os
import pickle
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO, format="%(asctime)s [MODEL] %(message)s")
logger = logging.getLogger(__name__)

class UserBasedRecommender:
    """
    Recommandeur basé sur la similarité cosinus entre utilisateurs.
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

    def fit(self, df: pd.DataFrame) -> "UserBasedRecommender":
        logger.info("Construction de la matrice utilisateur-item…")
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

        logger.info(f"  → Matrice : {matrix.shape[0]} utilisateurs × {matrix.shape[1]} livres")
        logger.info("Calcul de la matrice de similarité cosinus…")
        values = matrix.values.astype(float)
        self.similarity_matrix = cosine_similarity(values)
        logger.info("  → Similarité calculée.")
        return self

    def recommend(self, user_id: str, n: int | None = None) -> list[int]:
        n = n or self.n_recommendations
        if user_id not in self.user_index:
            logger.info(f"Utilisateur inconnu '{user_id}' → fallback popularité")
            return self._popular_books(n)

        user_idx = self.user_index[user_id]
        sim_scores = self.similarity_matrix[user_idx]
        neighbor_indices = np.argsort(sim_scores)[::-1]
        neighbor_indices = [i for i in neighbor_indices if i != user_idx][:self.n_neighbors]

        user_row = self.user_item_matrix.values[user_idx]
        already_read = set(np.where(user_row > 0)[0])

        scores = np.zeros(self.user_item_matrix.shape[1])
        sim_sum = np.zeros(self.user_item_matrix.shape[1])

        for neighbor_idx in neighbor_indices:
            sim = sim_scores[neighbor_idx]
            neighbor_row = self.user_item_matrix.values[neighbor_idx]
            scores += sim * neighbor_row
            sim_sum += np.where(neighbor_row > 0, sim, 0)

        with np.errstate(divide="ignore", invalid="ignore"):
            normalized = np.where(sim_sum > 0, scores / sim_sum, 0)

        for idx in already_read:
            normalized[idx] = 0.0

        top_indices = np.argsort(normalized)[::-1][:n]
        top_indices = [i for i in top_indices if normalized[i] > 0]

        if len(top_indices) < n:
            popular = self._popular_books(n, exclude=already_read)
            seen_ids = {self.reverse_item_index[i] for i in top_indices}
            extras = [bid for bid in popular if bid not in seen_ids]
            result_ids = [self.reverse_item_index[i] for i in top_indices]
            result_ids += extras[: n - len(result_ids)]
            return result_ids

        return [self.reverse_item_index[i] for i in top_indices]

    def _popular_books(self, n: int, exclude: set = None) -> list[int]:
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
