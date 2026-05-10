from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# ─────────────────────────────────────────────────────────────────
# Schémas de réponse
# ─────────────────────────────────────────────────────────────────

class RecommandationResponse(BaseModel):
    """Liste des IDs de livres recommandés pour un utilisateur."""
    utilisateur_id: str
    livre_ids: List[int]
    source: str = "model"  # "model" | "popular" | "no_data"


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_path: str


class TrainingResponse(BaseModel):
    status: str
    message: str
    metrics: Optional[dict] = None


class ModelInfoResponse(BaseModel):
    model_loaded: bool
    n_users: int
    n_books: int
    model_path: str


# ─────────────────────────────────────────────────────────────────
# Historique d'entraînement (lié à la DB)
# ─────────────────────────────────────────────────────────────────

class TrainingHistoryResponse(BaseModel):
    id: int
    version: str
    date_entrainement: datetime
    status: str
    metrics: Optional[str] = None

    class Config:
        from_attributes = True
