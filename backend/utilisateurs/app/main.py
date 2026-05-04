from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from . import models, schemas
from .database import engine, get_db

# Création de toutes les tables dans la base de données
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Service Utilisateurs",
    description="Gestion des profils, identités et rôles des utilisateurs de la bibliothèque.",
    version="1.0.0"
)

# HELPER — Hachage de mot de passe (simplifié)


def fake_hash(password: str) -> str:
    """Remplacer par passlib/bcrypt en production."""
    return password + "_hashed"


# HELPER — Création atomique du sous-profil

def _create_sous_profil(db: Session, utilisateur: models.Utilisateur, data: schemas.UtilisateurCreate):
    """Crée le sous-profil correspondant au type de l'utilisateur, dans la même transaction."""
    t = utilisateur.type_utilisateur

    if t == models.TypeUtilisateur.etudiant:
        profil = data.profil_etudiant or schemas.EtudiantProfile()
        db.add(models.Etudiant(
            id_utilisateur=utilisateur.id_utilisateur,
            numero_etudiant=profil.numero_etudiant,
            filiere=profil.filiere,
            niveau=profil.niveau,
        ))

    elif t == models.TypeUtilisateur.professeur:
        profil = data.profil_professeur or schemas.ProfesseurProfile()
        db.add(models.Professeur(
            id_utilisateur=utilisateur.id_utilisateur,
            specialite=profil.specialite,
            departement=profil.departement,
        ))

    elif t == models.TypeUtilisateur.personnel:
        profil = data.profil_personnel or schemas.PersonnelProfile()
        db.add(models.Personnel(
            id_utilisateur=utilisateur.id_utilisateur,
            poste=profil.poste,
            departement=profil.departement,
        ))

    elif t == models.TypeUtilisateur.admin:
        db.add(models.Admin(id_utilisateur=utilisateur.id_utilisateur))


# POST /utilisateurs/ — Créer un utilisateur


@app.post(
    "/utilisateurs/",
    response_model=schemas.UtilisateurResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un utilisateur + son sous-profil en une transaction"
)
def create_utilisateur(data: schemas.UtilisateurCreate, db: Session = Depends(get_db)):
    # Vérifier unicité email
    if db.query(models.Utilisateur).filter(models.Utilisateur.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email déjà enregistré.")

    # Vérifier unicité téléphone (si fourni)
    if data.numero_telephone:
        if db.query(models.Utilisateur).filter(
            models.Utilisateur.numero_telephone == data.numero_telephone
        ).first():
            raise HTTPException(status_code=400, detail="Numéro de téléphone déjà utilisé.")

    # Créer l'utilisateur central
    utilisateur = models.Utilisateur(
        email=data.email,
        numero_telephone=data.numero_telephone,
        mot_de_passe_hash=fake_hash(data.mot_de_passe),
        nom_prenom=data.nom_prenom,
        type_utilisateur=data.type_utilisateur,
        status=models.StatusUtilisateur.actif,
    )
    db.add(utilisateur)
    db.flush()  # Obtenir l'UUID sans commit pour l'utiliser dans le sous-profil

    # Créer le sous-profil dans la même transaction
    _create_sous_profil(db, utilisateur, data)

    db.commit()
    db.refresh(utilisateur)
    return utilisateur


# GET /utilisateurs/ — Lister tous les utilisateurs


@app.get(
    "/utilisateurs/",
    response_model=List[schemas.UtilisateurResponse],
    summary="Lister tous les utilisateurs avec pagination"
)
def list_utilisateurs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(models.Utilisateur).offset(skip).limit(limit).all()



# GET /utilisateurs/{id} — Détail d'un utilisateur


@app.get(
    "/utilisateurs/{utilisateur_id}",
    response_model=schemas.UtilisateurResponse,
    summary="Récupérer un utilisateur par son UUID"
)
def get_utilisateur(utilisateur_id: UUID, db: Session = Depends(get_db)):
    utilisateur = db.query(models.Utilisateur).filter(
        models.Utilisateur.id_utilisateur == utilisateur_id
    ).first()
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    return utilisateur



# GET /utilisateurs/type/{type} — Filtrer par type


@app.get(
    "/utilisateurs/type/{type_utilisateur}",
    response_model=List[schemas.UtilisateurResponse],
    summary="Filtrer les utilisateurs par type (ETUDIANT, PROFESSEUR, PERSONNEL, ADMIN)"
)
def list_by_type(type_utilisateur: models.TypeUtilisateur, db: Session = Depends(get_db)):
    return db.query(models.Utilisateur).filter(
        models.Utilisateur.type_utilisateur == type_utilisateur
    ).all()


# PUT /utilisateurs/{id} — Modifier un utilisateur


@app.put(
    "/utilisateurs/{utilisateur_id}",
    response_model=schemas.UtilisateurResponse,
    summary="Modifier les informations d'un utilisateur et/ou son sous-profil"
)
def update_utilisateur(
    utilisateur_id: UUID,
    data: schemas.UtilisateurUpdate,
    db: Session = Depends(get_db)
):
    utilisateur = db.query(models.Utilisateur).filter(
        models.Utilisateur.id_utilisateur == utilisateur_id
    ).first()
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")

    # Mise à jour des champs de la table centrale
    if data.nom_prenom is not None:
        utilisateur.nom_prenom = data.nom_prenom
    if data.numero_telephone is not None:
        utilisateur.numero_telephone = data.numero_telephone
    if data.status is not None:
        utilisateur.status = data.status

    # Mise à jour du sous-profil étudiant
    if data.profil_etudiant and utilisateur.etudiant:
        p = utilisateur.etudiant
        if data.profil_etudiant.numero_etudiant is not None:
            p.numero_etudiant = data.profil_etudiant.numero_etudiant
        if data.profil_etudiant.filiere is not None:
            p.filiere = data.profil_etudiant.filiere
        if data.profil_etudiant.niveau is not None:
            p.niveau = data.profil_etudiant.niveau

    # Mise à jour du sous-profil professeur
    if data.profil_professeur and utilisateur.professeur:
        p = utilisateur.professeur
        if data.profil_professeur.specialite is not None:
            p.specialite = data.profil_professeur.specialite
        if data.profil_professeur.departement is not None:
            p.departement = data.profil_professeur.departement

    # Mise à jour du sous-profil personnel
    if data.profil_personnel and utilisateur.personnel:
        p = utilisateur.personnel
        if data.profil_personnel.poste is not None:
            p.poste = data.profil_personnel.poste
        if data.profil_personnel.departement is not None:
            p.departement = data.profil_personnel.departement

    db.commit()
    db.refresh(utilisateur)
    return utilisateur


# DELETE /utilisateurs/{id} — Désactiver (soft delete)


@app.delete(
    "/utilisateurs/{utilisateur_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un utilisateur (soft delete → status SUPPRIME)"
)
def delete_utilisateur(utilisateur_id: UUID, db: Session = Depends(get_db)):
    utilisateur = db.query(models.Utilisateur).filter(
        models.Utilisateur.id_utilisateur == utilisateur_id
    ).first()
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")

    # Soft delete : on ne supprime pas physiquement, on change le status
    utilisateur.status = models.StatusUtilisateur.supprime
    db.commit()
    return None
