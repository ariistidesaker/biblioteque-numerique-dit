from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from . import models, schemas
from .database import engine, get_db

# Création des tables
models.Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Service Livres",
    description="Gestion du catalogue de la bibliothèque académique : ajout, modification, suppression et recherche de livres.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ══════════════════════════════════════════════
# POST /livres/ — Ajouter un livre
# ══════════════════════════════════════════════

@app.post(
    "/livres/",
    response_model=schemas.LivreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un nouveau livre au catalogue"
)
def create_livre(livre: schemas.LivreCreate, db: Session = Depends(get_db)):
    # Vérifier unicité de l'ISBN
    if db.query(models.Livre).filter(models.Livre.isbn == livre.isbn).first():
        raise HTTPException(status_code=400, detail=f"Un livre avec l'ISBN '{livre.isbn}' existe déjà.")

    db_livre = models.Livre(
        titre=livre.titre,
        auteur=livre.auteur,
        isbn=livre.isbn,
        description=livre.description,
        image_url=livre.image_url,
        exemplaires_totaux=livre.exemplaires_totaux,
        categorie=livre.categorie,
        disponible=livre.exemplaires_totaux > 0,
    )
    db.add(db_livre)
    db.commit()
    db.refresh(db_livre)
    return db_livre


# ══════════════════════════════════════════════
# GET /livres/ — Lister tous les livres
# ══════════════════════════════════════════════

@app.get(
    "/livres/",
    response_model=List[schemas.LivreResponse],
    summary="Lister tous les livres avec pagination"
)
def list_livres(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à ignorer"),
    limit: int = Query(100, ge=1, le=500, description="Nombre max d'éléments à retourner"),
    categorie: Optional[str] = Query(None, description="Filtrer par catégorie"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Livre)
    if categorie:
        query = query.filter(models.Livre.categorie == categorie)
    return query.offset(skip).limit(limit).all()


# ══════════════════════════════════════════════
# GET /livres/recherche — Recherche multicritères
# ══════════════════════════════════════════════

@app.get(
    "/livres/recherche",
    response_model=List[schemas.LivreResponse],
    summary="Rechercher des livres par titre, auteur ou ISBN"
)
def recherche_livres(
    titre: Optional[str] = Query(None, description="Filtre par titre"),
    auteur: Optional[str] = Query(None, description="Filtre par auteur"),
    isbn: Optional[str] = Query(None, description="Filtre par ISBN"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Livre)
    
    if titre:
        query = query.filter(models.Livre.titre.ilike(f"%{titre}%"))
    if auteur:
        query = query.filter(models.Livre.auteur.ilike(f"%{auteur}%"))
    if isbn:
        query = query.filter(models.Livre.isbn.ilike(f"%{isbn}%"))
        
    return query.all()


# ══════════════════════════════════════════════
# GET /livres/{id} — Détail d'un livre
# ══════════════════════════════════════════════

@app.get(
    "/livres/{livre_id}",
    response_model=schemas.LivreResponse,
    summary="Récupérer un livre par son ID"
)
def get_livre(livre_id: int, db: Session = Depends(get_db)):
    livre = db.query(models.Livre).filter(models.Livre.id == livre_id).first()
    if not livre:
        raise HTTPException(status_code=404, detail="Livre non trouvé.")
    return livre


# ══════════════════════════════════════════════
# PUT /livres/{id} — Modifier un livre
# ══════════════════════════════════════════════

@app.put(
    "/livres/{livre_id}",
    response_model=schemas.LivreResponse,
    summary="Modifier les informations d'un livre"
)
def update_livre(livre_id: int, data: schemas.LivreUpdate, db: Session = Depends(get_db)):
    livre = db.query(models.Livre).filter(models.Livre.id == livre_id).first()
    if not livre:
        raise HTTPException(status_code=404, detail="Livre non trouvé.")

    # Vérifier unicité du nouvel ISBN si modifié
    if data.isbn and data.isbn != livre.isbn:
        if db.query(models.Livre).filter(models.Livre.isbn == data.isbn).first():
            raise HTTPException(status_code=400, detail=f"Un livre avec l'ISBN '{data.isbn}' existe déjà.")

    if data.titre is not None:
        livre.titre = data.titre
    if data.auteur is not None:
        livre.auteur = data.auteur
    if data.isbn is not None:
        livre.isbn = data.isbn
    if data.description is not None:
        livre.description = data.description
    if data.image_url is not None:
        livre.image_url = data.image_url
    if data.categorie is not None:
        livre.categorie = data.categorie
    if data.exemplaires_totaux is not None:
        livre.exemplaires_totaux = data.exemplaires_totaux
        # Mise à jour automatique de la disponibilité
        livre.disponible = livre.exemplaires_totaux > 0
    elif data.disponible is not None:
        livre.disponible = data.disponible

    db.commit()
    db.refresh(livre)
    return livre


# ══════════════════════════════════════════════
# DELETE /livres/{id} — Supprimer un livre
# ══════════════════════════════════════════════

@app.delete(
    "/livres/{livre_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un livre du catalogue"
)
def delete_livre(livre_id: int, db: Session = Depends(get_db)):
    livre = db.query(models.Livre).filter(models.Livre.id == livre_id).first()
    if not livre:
        raise HTTPException(status_code=404, detail="Livre non trouvé.")

    db.delete(livre)
    db.commit()
    return None
