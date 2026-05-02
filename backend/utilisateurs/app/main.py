from fastapi import FastAPI
from . import models
from .database import engine

# Création des tables dans la base de données
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Service Utilisateurs")

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur le Service Utilisateurs"}
