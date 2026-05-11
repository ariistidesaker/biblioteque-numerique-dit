"""
main.py — Service Recommandation (FastAPI)

Endpoints :
    GET  /                              → Santé du service
    GET  /health                        → Statut détaillé + état du modèle
    GET  /recommandations/{user_id}     → Recommandations personnalisées
    GET  /recommandations/populaires    → Livres les plus populaires (fallback global)
    GET  /modele/info                   → Infos sur le modèle chargé
    POST /modele/entrainer              → Déclenche un ré-entraînement complet
    GET  /modele/historique             → Historique des entraînements
"""

import json
import logging
import os
import tempfile
from datetime import datetime
from typing import List, Optional

import httpx
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas
from .database import engine, get_db
from .model_loader import get_model, load_model, reload_model

# ─────────────────────────────────────────────────────────────────
# Init
# ─────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO, format="%(asctime)s [RECO-API] %(message)s")
logger = logging.getLogger(__name__)

# Création des tables
models.Base.metadata.create_all(bind=engine)

# URLs externes
EMPRUNTS_SERVICE_URL = os.getenv("EMPRUNTS_SERVICE_URL", "http://localhost:8003")
LIVRES_SERVICE_URL   = os.getenv("LIVRES_SERVICE_URL",   "http://localhost:8001")
MODEL_PATH           = os.getenv("MODEL_PATH", "/app/model/model.pkl")

# Application FastAPI
app = FastAPI(
    title="Service Recommandation",
    description="API de Machine Learning pour les recommandations personnalisées de livres.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────
# Événements du cycle de vie
# ─────────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup_event():
    """Charge le modèle au démarrage de l'application."""
    load_model()


# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────

def _fetch_popular_books(n: int = 5) -> List[int]:
    """
    Appelle le Service Livres pour récupérer les livres disponibles.
    Retourne les n premiers IDs (fallback simple).
    """
    try:
        resp = httpx.get(f"{LIVRES_SERVICE_URL}/livres/", timeout=5.0)
        resp.raise_for_status()
        livres = resp.json()
        # On prend les n premiers livres disponibles
        available = [l["id"] for l in livres if l.get("disponible", True)]
        return available[:n]
    except Exception as exc:
        logger.warning(f"Impossible de récupérer les livres populaires : {exc}")
        return []


def _run_training_pipeline(db: Session, version: str) -> dict:
    """
    Exécute le pipeline ML complet :
      1. Télécharge l'export CSV depuis le service Emprunts
      2. Prétraite les données (process.py)
      3. Entraîne le modèle (train.py)
      4. Évalue le modèle (evaluate.py)
      5. Recharge le modèle en mémoire
      6. Enregistre l'historique en base

    Retourne un dict avec status et metrics.
    """
    from .ml.process import clean_and_feature_engineer, generate_synthetic_data
    from .ml.model import UserBasedRecommender
    from .ml.evaluate import evaluate

    import pandas as pd
    from io import StringIO

    history_entry = models.ModelTrainingHistory(
        version=version,
        date_entrainement=datetime.utcnow(),
        status="running",
    )
    db.add(history_entry)
    db.commit()
    db.refresh(history_entry)

    try:
        # ── 1. Récupérer les données depuis le service Emprunts ──
        logger.info("Téléchargement des données depuis le service Emprunts…")
        try:
            resp = httpx.get(f"{EMPRUNTS_SERVICE_URL}/emprunts/export", timeout=30.0)
            resp.raise_for_status()
            raw_csv = resp.text
            df_raw = pd.read_csv(StringIO(raw_csv))
            logger.info(f"  → {len(df_raw)} emprunts récupérés.")
        except Exception as exc:
            logger.warning(f"Service Emprunts indisponible : {exc}. Utilisation de données synthétiques.")
            df_raw = None

        # ── 2. Prétraitement ──────────────────────────────────────
        if df_raw is not None and not df_raw.empty:
            df_processed = clean_and_feature_engineer(df_raw)
        else:
            logger.info("Génération de données synthétiques pour l'entraînement.")
            df_processed = generate_synthetic_data()

        if df_processed.empty:
            raise ValueError("Aucune donnée disponible pour l'entraînement.")

        # ── 3. Entraînement ───────────────────────────────────────
        logger.info("Entraînement du modèle…")
        model = UserBasedRecommender(n_neighbors=10, n_recommendations=5)
        model.fit(df_processed)

        # ── 4. Évaluation ─────────────────────────────────────────
        logger.info("Évaluation du modèle…")
        metrics = evaluate(model, df_processed, k=5)

        # ── 5. Sauvegarde ─────────────────────────────────────────
        os.makedirs(os.path.dirname(MODEL_PATH) if os.path.dirname(MODEL_PATH) else ".", exist_ok=True)
        model.save(MODEL_PATH)
        reload_model()
        logger.info("Modèle sauvegardé et rechargé en mémoire.")

        # ── 6. Enregistrement historique ──────────────────────────
        history_entry.status = "success"
        history_entry.metrics = json.dumps(metrics)
        db.commit()

        return {"status": "success", "metrics": metrics}

    except Exception as exc:
        logger.error(f"Erreur pendant l'entraînement : {exc}")
        history_entry.status = "failed"
        history_entry.metrics = json.dumps({"error": str(exc)})
        db.commit()
        return {"status": "failed", "metrics": {"error": str(exc)}}


# ─────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────

@app.get("/", tags=["Santé"])
def read_root():
    return {
        "service": "Service Recommandation",
        "version": "1.0.0",
        "status": "running",
        "model_loaded": get_model() is not None,
    }


@app.get("/health", response_model=schemas.HealthResponse, tags=["Santé"])
def health_check():
    """Vérification de l'état du service et du modèle ML."""
    return schemas.HealthResponse(
        status="ok",
        model_loaded=get_model() is not None,
        model_path=MODEL_PATH,
    )


# ──────────────────────────────────────────────────────────────────
# Recommandations
# ──────────────────────────────────────────────────────────────────

@app.get(
    "/recommandations/populaires",
    response_model=schemas.RecommandationResponse,
    tags=["Recommandations"],
    summary="Livres les plus populaires (sans personnalisation)"
)
def get_popular(n: int = Query(5, ge=1, le=20, description="Nombre de livres à retourner")):
    """
    Retourne les livres les plus populaires du catalogue.
    Utile pour les utilisateurs non connectés ou sans historique.
    """
    model = get_model()
    if model is not None:
        books = model._popular_books(n)
    else:
        books = _fetch_popular_books(n)

    return schemas.RecommandationResponse(
        utilisateur_id="anonymous",
        livre_ids=books,
        source="popular",
    )


@app.get(
    "/recommandations/{utilisateur_id}",
    response_model=schemas.RecommandationResponse,
    tags=["Recommandations"],
    summary="Recommandations personnalisées pour un utilisateur"
)
def get_recommendations(
    utilisateur_id: str,
    n: int = Query(5, ge=1, le=20, description="Nombre de recommandations"),
):
    """
    Retourne les N livres recommandés pour l'utilisateur donné.

    - Si le modèle est chargé et que l'utilisateur est connu, utilise le filtrage collaboratif.
    - Sinon, retourne les livres les plus populaires en fallback.
    """
    model = get_model()

    if model is None:
        # Fallback : livres populaires via le service Livres
        books = _fetch_popular_books(n)
        return schemas.RecommandationResponse(
            utilisateur_id=utilisateur_id,
            livre_ids=books,
            source="popular",
        )

    # Recommandation personnalisée
    books = model.recommend(utilisateur_id, n=n)
    source = "model" if utilisateur_id in model.user_index else "popular"

    return schemas.RecommandationResponse(
        utilisateur_id=utilisateur_id,
        livre_ids=books,
        source=source,
    )


# ──────────────────────────────────────────────────────────────────
# Gestion du modèle
# ──────────────────────────────────────────────────────────────────

@app.get(
    "/modele/info",
    response_model=schemas.ModelInfoResponse,
    tags=["Modèle ML"],
    summary="Informations sur le modèle chargé"
)
def get_model_info():
    """Retourne des métadonnées sur le modèle actuellement en mémoire."""
    model = get_model()
    if model is None:
        return schemas.ModelInfoResponse(
            model_loaded=False,
            n_users=0,
            n_books=0,
            model_path=MODEL_PATH,
        )
    matrix = model.user_item_matrix
    return schemas.ModelInfoResponse(
        model_loaded=True,
        n_users=matrix.shape[0] if matrix is not None else 0,
        n_books=matrix.shape[1] if matrix is not None else 0,
        model_path=MODEL_PATH,
    )


@app.post(
    "/modele/entrainer",
    response_model=schemas.TrainingResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Modèle ML"],
    summary="Déclenche un ré-entraînement complet du modèle (en arrière-plan)"
)
def trigger_training(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Lance le pipeline d'entraînement ML en tâche de fond :
    téléchargement → prétraitement → entraînement → évaluation → rechargement.
    """
    version = datetime.utcnow().strftime("v%Y%m%d_%H%M%S")
    logger.info(f"Lancement du pipeline d'entraînement version {version}…")

    # On démarre en background pour ne pas bloquer la réponse
    background_tasks.add_task(_run_training_pipeline, db, version)

    return schemas.TrainingResponse(
        status="accepted",
        message=f"Entraînement {version} lancé en arrière-plan. Consultez /modele/historique pour le suivi.",
    )


@app.post(
    "/modele/entrainer/sync",
    response_model=schemas.TrainingResponse,
    tags=["Modèle ML"],
    summary="Ré-entraîne le modèle de manière synchrone (bloquant, pour les tests)"
)
def trigger_training_sync(db: Session = Depends(get_db)):
    """Même pipeline que /modele/entrainer mais bloquant (pratique pour les tests)."""
    version = datetime.utcnow().strftime("v%Y%m%d_%H%M%S")
    result = _run_training_pipeline(db, version)
    return schemas.TrainingResponse(
        status=result["status"],
        message=f"Entraînement {version} terminé.",
        metrics=result.get("metrics"),
    )


@app.get(
    "/modele/historique",
    response_model=List[schemas.TrainingHistoryResponse],
    tags=["Modèle ML"],
    summary="Historique des entraînements"
)
def get_training_history(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retourne les N derniers entraînements enregistrés en base."""
    history = (
        db.query(models.ModelTrainingHistory)
        .order_by(models.ModelTrainingHistory.date_entrainement.desc())
        .limit(limit)
        .all()
    )
    return history
