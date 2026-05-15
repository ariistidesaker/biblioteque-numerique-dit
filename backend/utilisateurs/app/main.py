from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from . import models, schemas
from .database import engine, get_db

# Création de toutes les tables dans la base de données
models.Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Service Utilisateurs",
    description="Gestion des profils, identités et rôles des utilisateurs de la bibliothèque.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En développement, on autorise tout. À restreindre en prod.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HELPER — Hachage de mot de passe (simplifié)


def fake_hash(password: str) -> str:
    """Remplacer par passlib/bcrypt en production."""
    return password + "_hashed"


# HELPER — Création atomique du sous-profil

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_real_email(to_email: str, subject: str, body: str):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER", "votre.email@gmail.com")
    smtp_password = os.getenv("SMTP_PASSWORD", "votre_mot_de_passe_app")
    from_email = os.getenv("SMTP_FROM", "no-reply@bibliotech.com")

    msg = MIMEMultipart()
    msg['From'] = f"BiblioTech <{from_email}>"
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # Si ce sont les valeurs par défaut, on affiche un avertissement clair
    if smtp_user == "votre.email@gmail.com" and smtp_server == "smtp.gmail.com":
        print(f"⚠️ SMTP non configuré. Les identifiants par défaut sont présents.")
        print(f"   Impossible d'envoyer l'email 'no-reply' à {to_email} sans un vrai serveur SMTP relais.")
        return

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        # On ne s'authentifie que si un utilisateur est fourni (certains relais SMTP internes n'en ont pas besoin)
        if smtp_user:
            server.login(smtp_user, smtp_password)
            
        server.send_message(msg)
        server.quit()
        print(f"✅ Email envoyé avec succès à {to_email} via {from_email}")
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de l'email à {to_email}: {e}")


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


import random

# POST /utilisateurs/ — Créer un utilisateur
@app.post(
    "/utilisateurs/",
    response_model=schemas.UtilisateurResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un utilisateur (avec envoi de code par mail)"
)
def create_utilisateur(data: schemas.UtilisateurCreate, db: Session = Depends(get_db)):
    if db.query(models.Utilisateur).filter(models.Utilisateur.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email déjà enregistré.")

    if data.numero_telephone:
        if db.query(models.Utilisateur).filter(models.Utilisateur.numero_telephone == data.numero_telephone).first():
            raise HTTPException(status_code=400, detail="Numéro de téléphone déjà utilisé.")

    # Génération du code de confirmation à 6 chiffres
    code = str(random.randint(100000, 999999))

    utilisateur = models.Utilisateur(
        email=data.email,
        numero_telephone=data.numero_telephone,
        mot_de_passe_hash=fake_hash(data.mot_de_passe),
        nom_prenom=data.nom_prenom,
        type_utilisateur=data.type_utilisateur,
        status=models.StatusUtilisateur.en_attente,
        code_confirmation=code
    )
    db.add(utilisateur)
    db.flush()

    _create_sous_profil(db, utilisateur, data)
    db.commit()
    db.refresh(utilisateur)

    # Envoi de l'email
    print(f"📧 [EMAIL] Tentative d'envoi à {data.email}...")
    sujet = "Votre code de confirmation BiblioTech"
    message = f"Bonjour {data.nom_prenom},\n\nVotre code de confirmation est : {code}\n\nMerci de vous être inscrit sur BiblioTech."
    print(f"   Sujet: {sujet}")
    print(f"   Message: {message}")
    send_real_email(data.email, sujet, message)

    return utilisateur

# POST /confirmer — Confirmer l'email
@app.post("/confirmer", summary="Confirmer l'inscription via le code reçu par mail")
def confirmer_email(data: schemas.ConfirmEmailRequest, db: Session = Depends(get_db)):
    utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.email == data.email).first()
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    
    if utilisateur.status == models.StatusUtilisateur.actif:
        return {"message": "Compte déjà activé."}
        
    if utilisateur.code_confirmation != data.code:
        raise HTTPException(status_code=400, detail="Code de confirmation invalide.")
        
    # Activation du compte
    utilisateur.status = models.StatusUtilisateur.actif
    utilisateur.code_confirmation = None
    db.commit()
    return {"message": "Compte activé avec succès !"}

# POST /login — Authentification
@app.post(
    "/login",
    response_model=schemas.UtilisateurResponse,
    summary="Authentifier un utilisateur (Login)"
)
def login(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    utilisateur = db.query(models.Utilisateur).filter(
        models.Utilisateur.email == credentials.email
    ).first()
    
    if not utilisateur:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect.")
    
    if utilisateur.status != models.StatusUtilisateur.actif:
        raise HTTPException(status_code=403, detail="Ce compte est inactif ou supprimé.")
        
    expected_hash = fake_hash(credentials.mot_de_passe)
    if utilisateur.mot_de_passe_hash != expected_hash:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect.")
        
    # En production, on retournerait un token JWT ici. Pour l'instant on retourne le profil.
    return utilisateur


# POST /mot-de-passe-oublie — Réinitialisation
@app.post(
    "/mot-de-passe-oublie",
    summary="Demander une réinitialisation de mot de passe"
)
def forgot_password(data: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    utilisateur = db.query(models.Utilisateur).filter(
        models.Utilisateur.email == data.email
    ).first()
    
    if utilisateur:
        # Simulation de l'envoi d'email
        reset_token = str(random.randint(100000, 999999))
        utilisateur.code_confirmation = reset_token
        db.commit()

        # Envoi de l'email
        print(f"📧 [EMAIL] Tentative d'envoi à {data.email}...")
        sujet = "Réinitialisation de votre mot de passe BiblioTech"
        lien = f"http://localhost:5173/reset-password?token={reset_token}"
        message = f"Bonjour {utilisateur.nom_prenom},\n\nPour réinitialiser votre mot de passe, veuillez cliquer sur le lien suivant :\n{lien}\n\nSi vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet email."
        print(f"   Sujet: {sujet}")
        print(f"   Message: {message}")
        send_real_email(data.email, sujet, message)
    
    # On retourne un succès même si l'email n'existe pas (sécurité)
    return {"message": "Si cette adresse email existe, un lien de réinitialisation a été envoyé."}


# POST /reset-password — Appliquer le nouveau mot de passe
@app.post(
    "/reset-password",
    summary="Définir un nouveau mot de passe avec le token de réinitialisation"
)
def reset_password(data: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    # Chercher l'utilisateur avec ce token
    utilisateur = db.query(models.Utilisateur).filter(
        models.Utilisateur.code_confirmation == data.token
    ).first()

    if not utilisateur:
        raise HTTPException(status_code=400, detail="Lien de réinitialisation invalide ou expiré.")

    # Mettre à jour le mot de passe
    utilisateur.mot_de_passe_hash = fake_hash(data.nouveau_mot_de_passe)
    utilisateur.code_confirmation = None
    db.commit()

    return {"message": "Mot de passe réinitialisé avec succès."}


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
