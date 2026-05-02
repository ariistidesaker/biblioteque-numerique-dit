from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db

# Création des tables dans la base de données
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Service Utilisateurs")

# ---
# Endpoint : Création d'un utilisateur
# Rôle : Permet d'inscrire un nouvel utilisateur dans la base de données.
# Il vérifie d'abord que l'adresse email n'est pas déjà utilisée.
# ---
@app.post("/utilisateurs/", response_model=schemas.UtilisateurResponse)
def create_utilisateur(utilisateur: schemas.UtilisateurCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.Utilisateur).filter(models.Utilisateur.email == utilisateur.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")
    
    # Simulation de hachage de mot de passe (à remplacer par passlib/bcrypt pour la production)
    fake_hashed_password = utilisateur.mot_de_passe + "notreallyhashed"
    
    db_utilisateur = models.Utilisateur(
        nom=utilisateur.nom,
        email=utilisateur.email,
        type_utilisateur=utilisateur.type_utilisateur,
        mot_de_passe_hash=fake_hashed_password
    )
    db.add(db_utilisateur)
    db.commit()
    db.refresh(db_utilisateur)
    return db_utilisateur

# ---
# Endpoint : Récupérer la liste des utilisateurs
# Rôle : Renvoie tous les utilisateurs enregistrés avec une pagination optionnelle (skip, limit).
# ---
@app.get("/utilisateurs/", response_model=list[schemas.UtilisateurResponse])
def read_utilisateurs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    utilisateurs = db.query(models.Utilisateur).offset(skip).limit(limit).all()
    return utilisateurs

# ---
# Endpoint : Récupérer un utilisateur spécifique
# Rôle : Cherche et renvoie les détails d'un utilisateur grâce à son ID unique.
# Si l'ID n'existe pas, renvoie une erreur 404.
# ---
@app.get("/utilisateurs/{utilisateur_id}", response_model=schemas.UtilisateurResponse)
def read_utilisateur(utilisateur_id: int, db: Session = Depends(get_db)):
    db_utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.id == utilisateur_id).first()
    if db_utilisateur is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return db_utilisateur
