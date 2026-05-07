import os
import csv
import httpx
from io import StringIO
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from . import models, schemas
from .database import engine, get_db

# Création des tables
models.Base.metadata.create_all(bind=engine)

# URLs des services inter-microservices (via Docker network ou variables d'env)
LIVRES_SERVICE_URL       = os.getenv("LIVRES_SERVICE_URL", "http://localhost:8001")
UTILISATEURS_SERVICE_URL = os.getenv("UTILISATEURS_SERVICE_URL", "http://localhost:8002")

app = FastAPI(
    title="Service Emprunts",
    description="Gestion du cycle de vie des emprunts : emprunt, retour, historique, retards et export pour le ML.",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────
# HELPERS — Vérification cross-service via REST
# ──────────────────────────────────────────────

def verifier_livre_existe(livre_id: int):
    """Appel REST vers le Service Livres pour vérifier l'existence du livre."""
    try:
        response = httpx.get(f"{LIVRES_SERVICE_URL}/livres/{livre_id}", timeout=5.0)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Livre {livre_id} introuvable dans le catalogue.")
        response.raise_for_status()
        return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Service Livres indisponible.")


def verifier_utilisateur_existe(utilisateur_id: UUID):
    """Appel REST vers le Service Utilisateurs pour vérifier l'existence de l'utilisateur."""
    try:
        response = httpx.get(f"{UTILISATEURS_SERVICE_URL}/utilisateurs/{utilisateur_id}", timeout=5.0)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Utilisateur {utilisateur_id} introuvable.")
        response.raise_for_status()
        return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Service Utilisateurs indisponible.")


def mettre_a_jour_disponibilite_livre(livre_id: int, disponible: bool):
    """Appel REST vers le Service Livres pour mettre à jour la disponibilité."""
    try:
        response = httpx.put(
            f"{LIVRES_SERVICE_URL}/livres/{livre_id}",
            json={"disponible": disponible},
            timeout=5.0
        )
        response.raise_for_status()
    except httpx.RequestError:
        # On log l'erreur mais on ne bloque pas forcément si l'emprunt est déjà créé (à débattre)
        # Ici on préfère lever une exception pour garder la cohérence
        raise HTTPException(status_code=503, detail="Impossible de mettre à jour la disponibilité du livre.")


# ══════════════════════════════════════════════
# POST /emprunts/ — Emprunter un livre
# ══════════════════════════════════════════════

@app.post(
    "/emprunts/",
    response_model=schemas.EmpruntResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enregistrer un nouvel emprunt (vérifie l'existence et la disponibilité du livre)"
)
def create_emprunt(data: schemas.EmpruntCreate, db: Session = Depends(get_db)):
    # Vérifier que le livre et l'utilisateur existent (appels REST)
    livre = verifier_livre_existe(data.livre_id)
    verifier_utilisateur_existe(data.utilisateur_id)

    # Vérifier si le livre est disponible
    if not livre.get("disponible", True):
        raise HTTPException(status_code=400, detail="Ce livre n'est pas disponible pour l'emprunt.")

    # Vérifier que l'utilisateur n'a pas déjà ce livre en cours d'emprunt
    emprunt_actif = db.query(models.Emprunt).filter(
        models.Emprunt.livre_id == data.livre_id,
        models.Emprunt.utilisateur_id == data.utilisateur_id,
        models.Emprunt.date_retour_effective == None  # noqa: E711
    ).first()
    if emprunt_actif:
        raise HTTPException(status_code=400, detail="Cet utilisateur a déjà ce livre en cours d'emprunt.")

    emprunt = models.Emprunt(
        livre_id=data.livre_id,
        utilisateur_id=data.utilisateur_id,
        date_retour_prevue=data.date_retour_prevue,
    )
    db.add(emprunt)
    db.commit()
    db.refresh(emprunt)

    # Mettre à jour la disponibilité du livre
    mettre_a_jour_disponibilite_livre(data.livre_id, disponible=False)

    return emprunt


# ══════════════════════════════════════════════
# PUT /emprunts/{id}/retour — Retourner un livre
# ══════════════════════════════════════════════

@app.put(
    "/emprunts/{emprunt_id}/retour",
    response_model=schemas.EmpruntResponse,
    summary="Enregistrer le retour d'un livre et calculer automatiquement le retard"
)
def retourner_livre(emprunt_id: int, data: schemas.RetourRequest, db: Session = Depends(get_db)):
    emprunt = db.query(models.Emprunt).filter(models.Emprunt.id == emprunt_id).first()
    if not emprunt:
        raise HTTPException(status_code=404, detail="Emprunt non trouvé.")
    if emprunt.date_retour_effective is not None:
        raise HTTPException(status_code=400, detail="Ce livre a déjà été retourné.")

    date_retour = data.date_retour_effective or datetime.utcnow()
    emprunt.date_retour_effective = date_retour

    # Détection automatique du retard
    emprunt.en_retard = date_retour > emprunt.date_retour_prevue

    db.commit()
    db.refresh(emprunt)

    # Mettre à jour la disponibilité du livre
    mettre_a_jour_disponibilite_livre(emprunt.livre_id, disponible=True)

    return emprunt


# ══════════════════════════════════════════════
# GET /emprunts/ — Historique complet
# ══════════════════════════════════════════════

@app.get(
    "/emprunts/",
    response_model=List[schemas.EmpruntResponse],
    summary="Lister tous les emprunts (historique complet), filtrable par utilisateur, livre ou statut"
)
def list_emprunts(
    utilisateur_id: Optional[UUID] = Query(None, description="Filtrer par UUID d'utilisateur"),
    livre_id: Optional[int] = Query(None, description="Filtrer par ID de livre"),
    statut: Optional[str] = Query(None, description="Filtrer par statut ('en_cours', 'retourne', 'en_retard')"),
    skip: int = Query(0, description="Pagination: offset"),
    limit: int = Query(100, description="Pagination: limite"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Emprunt)

    if utilisateur_id:
        query = query.filter(models.Emprunt.utilisateur_id == utilisateur_id)
    if livre_id:
        query = query.filter(models.Emprunt.livre_id == livre_id)
    
    if statut == 'en_cours':
        query = query.filter(models.Emprunt.date_retour_effective == None)
    elif statut == 'retourne':
        query = query.filter(models.Emprunt.date_retour_effective != None)
    elif statut == 'en_retard':
        query = query.filter(models.Emprunt.en_retard == True)

    return query.order_by(models.Emprunt.date_emprunt.desc()).offset(skip).limit(limit).all()


# ══════════════════════════════════════════════
# GET /emprunts/retards — Emprunts en retard
# ══════════════════════════════════════════════

@app.get(
    "/emprunts/retards",
    response_model=List[schemas.EmpruntResponse],
    summary="Lister les emprunts en retard (non retournés après la date prévue)"
)
def list_retards(db: Session = Depends(get_db)):
    maintenant = datetime.utcnow()
    return db.query(models.Emprunt).filter(
        models.Emprunt.date_retour_effective == None,       # noqa: E711
        models.Emprunt.date_retour_prevue < maintenant
    ).all()


# ══════════════════════════════════════════════
# GET /emprunts/export — Export CSV pour le ML
# ══════════════════════════════════════════════

@app.get(
    "/emprunts/export",
    summary="Exporter l'historique des emprunts en CSV (utilisé pour le pipeline DVC/ML)"
)
def export_csv(db: Session = Depends(get_db)):
    emprunts = db.query(models.Emprunt).all()

    output = StringIO()
    writer = csv.writer(output)
    # En-têtes
    writer.writerow(["id", "utilisateur_id", "livre_id", "date_emprunt", "date_retour_prevue", "date_retour_effective", "en_retard"])

    for e in emprunts:
        writer.writerow([
            e.id,
            str(e.utilisateur_id),
            e.livre_id,
            e.date_emprunt.isoformat() if e.date_emprunt else "",
            e.date_retour_prevue.isoformat() if e.date_retour_prevue else "",
            e.date_retour_effective.isoformat() if e.date_retour_effective else "",
            e.en_retard,
        ])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=loans.csv"}
    )


# ══════════════════════════════════════════════
# GET /emprunts/utilisateur/{user_id} — Par utilisateur
# ══════════════════════════════════════════════

@app.get(
    "/emprunts/utilisateur/{utilisateur_id}",
    response_model=List[schemas.EmpruntResponse],
    summary="Lister l'historique des emprunts d'un utilisateur spécifique"
)
def list_emprunts_utilisateur(utilisateur_id: UUID, db: Session = Depends(get_db)):
    return db.query(models.Emprunt).filter(
        models.Emprunt.utilisateur_id == utilisateur_id
    ).order_by(models.Emprunt.date_emprunt.desc()).all()
