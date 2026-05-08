#!/bin/bash

# Chargement des variables d'environnement depuis le fichier .env à la racine
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✅ Variables d'environnement chargées depuis .env"
else
    echo "⚠️ Fichier .env non trouvé à la racine. Utilisation des valeurs par défaut."
    # Valeurs par défaut si le fichier .env est absent
    DB_HOST=${DB_HOST:-localhost}
    DB_PORT=${DB_PORT:-5433}
    DB_USER=${DB_USER:-library_user}
    DB_PASS=${DB_PASS:-library_pass}
fi

echo "🚀 Démarrage de la Base de Données PostgreSQL..."
docker compose up -d db

echo "Attente de 10 secondes pour l'initialisation de la DB..."
sleep 10

echo "📚 Lancement du Service Livres (Port 8001)..."
cd backend/livres
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
export DATABASE_URL="postgresql+psycopg://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/livres_db"
uvicorn app.main:app --reload --port 8001 &
LIVRES_PID=$!
cd ../..

echo "👥 Lancement du Service Utilisateurs (Port 8002)..."
cd backend/utilisateurs
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
export DATABASE_URL="postgresql+psycopg://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/utilisateurs_db"
uvicorn app.main:app --reload --port 8002 &
UTILISATEURS_PID=$!
cd ../..

echo "🔄 Lancement du Service Emprunts (Port 8003)..."
cd backend/emprunts
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
export DATABASE_URL="postgresql+psycopg://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/emprunts_db"
export LIVRES_SERVICE_URL="http://localhost:8001"
export UTILISATEURS_SERVICE_URL="http://localhost:8002"
uvicorn app.main:app --reload --port 8003 &
EMPRUNTS_PID=$!
cd ../..

echo "🤖 Lancement du Service Recommandation (Port 8004)..."
cd backend/recommandation
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
export DATABASE_URL="postgresql+psycopg://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/recommandation_db"
uvicorn app.main:app --reload --port 8004 &
RECO_PID=$!
cd ../..

echo "🌐 Lancement du Frontend..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Tous les services sont lancés dans ce terminal !"
echo "⚠️ Appuyez sur CTRL+C pour tout arrêter proprement."
echo ""

cleanup() {
    echo ""
    echo "🛑 Arrêt de tous les services en cours..."
    kill $LIVRES_PID $UTILISATEURS_PID $EMPRUNTS_PID $RECO_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM
wait
