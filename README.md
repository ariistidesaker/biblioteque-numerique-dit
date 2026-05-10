# Bibliothèque Numérique Académique

Une plateforme complète et moderne de gestion de bibliothèque académique, conçue selon une architecture logicielle en **microservices**.

## Architecture 🏗️

Le backend est découpé en plusieurs microservices indépendants. Pour garantir une isolation parfaite et respecter les bonnes pratiques DevOps, le projet utilise le pattern **Database-per-service** (chaque microservice possède sa propre base de données PostgreSQL isolée) :

1. 📚 **Service Livres (Port `8001`)**
   - *Rôle* : Gestion du catalogue.
   - *Fonctionnalités* : Ajouter, modifier, supprimer, lister, rechercher par titre/auteur/ISBN.
   
2. 👥 **Service Utilisateurs (Port `8002`)**
   - *Rôle* : Gestion des profils et des identités.
   - *Fonctionnalités* : Inscription, rôles (Étudiant, Professeur, Personnel), consultation de profils.

3. 🔄 **Service Emprunts (Port `8003`)**
   - *Rôle* : Cœur du métier de la bibliothèque.
   - *Fonctionnalités* : Emprunter, retourner, historique, détection de retards, export pour le Machine Learning.

4. 🤖 **Service Recommandation (Port `8004`)**
   - *Rôle* : API de Machine Learning.
   - *Fonctionnalités* : Expose des recommandations personnalisées de livres, et gère le ré-entraînement du modèle ML.

5. 🌐 **Frontend**
   - Interface utilisateur web pour interagir avec l'ensemble des services.

---

## Structure du projet

Dans ce dépôt les microservices FastAPI vivent sous `backend/` (équivalent logique du dossier `services/` dans un schéma type cours).

```
bibliotheque-numerique-dit/
│
├── frontend/                           # Application React (Vite)
│   ├── public/
│   │   └── favicon.svg                  # Icônes / assets statiques
│   ├── src/
│   │   ├── components/                  # Composants réutilisables (à structurer selon le besoin)
│   │   ├── pages/                       # Pages (Catalogue, Profil, Admin…)
│   │   ├── services/                   # Fonctions d’appels API (livres, emprunts, reco…)
│   │   ├── assets/
│   │   ├── App.jsx                     # Racine UI
│   │   └── main.jsx                    # Point d’entrée Vite
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile                      # Multi-stage possible (build Node + serveur Nginx)
│
├── backend/                            # Microservices FastAPI
│   ├── livres/
│   │   ├── app/
│   │   │   ├── main.py                 # Application FastAPI, routes CRUD + recherche
│   │   │   ├── models.py               # Modèle SQLAlchemy Livre
│   │   │   ├── schemas.py              # Schémas Pydantic
│   │   │   ├── database.py             # Connexion PostgreSQL / SQLAlchemy
│   │   │   └── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── utilisateurs/
│   │   ├── app/
│   │   │   ├── main.py                 # Routes utilisateurs (CRUD, gestion types)
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── database.py
│   │   │   └── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── emprunts/
│   │   ├── app/
│   │   │   ├── main.py                 # Routes emprunts, retours, historique, export
│   │   │   ├── models.py
│   │   │   ├── schemas.py              # Schémas de données (Pydantic)
│   │   │   ├── database.py
│   │   │   └── requirements.txt
│   │   └── Dockerfile
│   │
│   └── recommandation/
│       ├── app/
│       │   ├── main.py                 # API FastAPI (Recommandations personnalisées, Santé, Entraînement)
│       │   ├── models.py               # SQLAlchemy (Historique d'entraînement)
│       │   ├── schemas.py              # Schémas Pydantic de réponse
│       │   ├── database.py             # Connexion PostgreSQL (suivi des versions)
│       │   ├── model_loader.py         # Chargement paresseux (lazy loading) du modèle ML
│       │   ├── ml/                     # Pipeline Machine Learning (DVC)
│       │   │   ├── __init__.py
│       │   │   ├── process.py          # Prétraitement et Feature Engineering
│       │   │   ├── train.py            # Entraînement (User-Based Collaborative Filtering)
│       │   │   └── evaluate.py         # Évaluation des performances (Précision, Recall, Couverture)
│       │   ├── __init__.py
│       │   └── requirements.txt        # Dépendances ML (scikit-learn, pandas, numpy...)
│       └── Dockerfile
│
├── data/                               # Données d'entraînement (raw_loans.csv, processed_loans.csv)
│   └── (fichiers CSV ou pointeurs .dvc)
│
├── models/                             # Modèle ML et métriques
│   ├── model.pkl                       # Modèle entraîné (suivi par DVC)
│   └── metrics.json                    # Résultats de l'évaluation (suivis par DVC)
│
├── db/
│   └── init.sql                        # Script d’init au démarrage Postgres (création des bases)
│
├── docker-compose.yml                  # db + livres + utilisateurs + emprunts + reco-api + frontend
├── start-local.sh                      # Développement : DB Docker + APIs + frontend locaux
├── .gitignore
├── dvc.yml                             # Pipeline DVC (référencé par le projet)
├── dvc.lock                            # Versions / hashs (auto-généré)
├── .dvc/
│   └── config
├── README.md
└── rapport.pdf                         # Facultatif (livrable, peut être fourni hors dépôt)
```

> **Note.** Les dossiers `frontend/src/components`, `pages` et `services` sont une organisation conseillée : vous pouvez les créer progressivement même s’ils ne sont pas encore tous présents.

---

## Technologies utilisées 🛠️

- **Backend** : FastAPI (Python 3.11), Uvicorn, SQLAlchemy (ORM), Pydantic.
- **Machine Learning** : Scikit-Learn, Pandas, NumPy, Joblib.
- **Base de données** : PostgreSQL (Images Docker).
- **Infrastucture** : Docker & Docker Compose.

---

## ⚙️ Installation Initiale (Pré-requis)

Si c'est la toute première fois que vous clonez le projet, vous devez installer les dépendances de chaque microservice pour pouvoir développer en local :

**1. Pour les microservices Backend (à faire 4 fois) :**
Naviguez dans `backend/livres`, `backend/utilisateurs`, `backend/emprunts` et `backend/recommandation` et exécutez ces commandes :
```bash
# Exemple pour le service Livres
cd backend/livres
python -m venv venv

# Activer (Git Bash / Linux / Mac)
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate

# Installer les dépendances
pip install -r app/requirements.txt
cd ../..
```

**2. Pour le Frontend :**
```bash
cd frontend
npm install
cd ..
```

---

## 🔐 Configuration des Variables d'Environnement

Le projet utilise un fichier `.env` à la racine pour centraliser toutes les configurations. Ce fichier est indispensable pour le bon fonctionnement des services.

1. Créez un fichier `.env` à la racine du projet (copiez le contenu ci-dessous ou utilisez `.env.example` s'il est fourni) :

```env
# Configuration de la Base de Données (Locale)
DB_HOST=localhost
DB_PORT=5433
DB_USER=library_user
DB_PASS=library_pass

# URLs des Microservices (Backend)
LIVRES_SERVICE_URL=http://localhost:8001
UTILISATEURS_SERVICE_URL=http://localhost:8002
EMPRUNTS_SERVICE_URL=http://localhost:8003
RECOMMANDATION_SERVICE_URL=http://localhost:8004

# Variables d'environnement pour le Frontend (Vite)
VITE_LIVRES_API_URL=http://localhost:8001
VITE_UTILISATEURS_API_URL=http://localhost:8002
VITE_EMPRUNTS_API_URL=http://localhost:8003
VITE_RECOMMANDATION_API_URL=http://localhost:8004
```

> [!IMPORTANT]
> Pour des raisons de sécurité, les URLs de base de données ne sont plus codées en dur dans le code. Si le fichier `.env` n'est pas correctement configuré, les services backend ne démarreront pas.

---

## 🚀 Démarrage Rapide (Mode Développement)

Pour développer et tester les APIs avec rechargement à chaud (Hot-Reload) :

1. Assurez-vous d'avoir **Docker**, **Git Bash** et **Python 3.11+** installés.
2. Ouvrez un terminal **PowerShell** à la racine du projet.
3. Exécutez le script d'automatisation (depuis Git Bash, WSL ou macOS/Linux) :

```bash
bash start-local.sh
```

**Que fait ce script ?**
- Lance la base de données PostgreSQL en arrière-plan via Docker.
- Utilise les environnements virtuels de chaque microservice.
- Lance les 4 APIs FastAPI sur les ports `8001` à `8004`.
- Lance le frontend Vite.
- Exécute tout dans le meme terminal (arrêt avec `CTRL+C`).

**Adresses Locales des Services**
- **Base PostgreSQL** : `localhost:5433` (mappage `5433 -> 5432` dans le conteneur).
- **Service Livres (API & Swagger Docs)** : [http://localhost:8001/docs](http://localhost:8001/docs)
- **Service Utilisateurs (API & Swagger Docs)** : [http://localhost:8002/docs](http://localhost:8002/docs)
- **Service Emprunts (API & Swagger Docs)** : [http://localhost:8003/docs](http://localhost:8003/docs)
- **Service Recommandation (API & Swagger Docs)** : [http://localhost:8004/docs](http://localhost:8004/docs)
- **Frontend (Interface Utilisateur)** : [http://localhost:5173](http://localhost:5173) *(Port par défaut de Vite, vérifiez votre terminal)*

### Arret des services

- Appuyez sur `CTRL+C` dans le terminal qui execute `bash start-local.sh`.

### Lancer un seul service manuellement (PowerShell)

Si vous souhaitez isoler le développement et ne lancer qu'un seul service (ex: Utilisateurs), ouvrez un terminal PowerShell et suivez ces étapes :

```powershell
# 1. Démarrer uniquement la base de données (si elle n'est pas déjà allumée)
docker compose up -d db

# 2. Se placer dans le dossier du service concerné
cd backend/utilisateurs

# 3. Définir l'URL de la base de données (manuellement ou via chargement du .env)
$env:DATABASE_URL="postgresql+psycopg://library_user:library_pass@localhost:5433/utilisateurs_db"

# 4. Lancer le serveur (Port 8002 pour Utilisateurs)
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8002
```
*(Adaptez le nom du dossier, le nom de la base `_db` et le port pour les autres services : Livres=8001, Emprunts=8003)*

---

## 🐳 Démarrage Complet (Mode Docker)

Pour exécuter toute l'infrastructure (bases de données + APIs encapsulées) de manière 100% conteneurisée :

```bash
docker compose up --build -d
```

Les bases de données s'initialiseront toutes seules et tous les services seront liés de façon transparente via le réseau virtuel de Docker.

Pour arreter :

```bash
docker compose down
```

---

## Depannage rapide

- **Erreur `password authentication failed for user library_user`** :
  - Verifiez que la base Docker tourne sur le port `5433` et pas `5432`.
  - Lancez `docker compose ps` et confirmez `0.0.0.0:5433->5432/tcp`.
- **Erreur `ModuleNotFoundError` sur un service** :
  - Reinstallez les dependances du service concerne :

```bash
./backend/<service>/venv/Scripts/pip.exe install -r backend/<service>/app/requirements.txt
```
