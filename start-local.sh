#!/bin/bash

echo "🚀 Démarrage de la Base de Données PostgreSQL..."
docker compose up -d db

echo "Attente de 10 secondes pour l'initialisation de la DB..."
sleep 10

echo "📚 Lancement du Service Livres (Port 8001)..."
cd backend/livres
# Compatible Windows (Git Bash) et Linux/Mac
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
export DATABASE_URL="postgresql+psycopg://library_user:library_pass@localhost:5433/livres_db"
uvicorn app.main:app --reload --port 8001 &
LIVRES_PID=$!
cd ../..

echo "👥 Lancement du Service Utilisateurs (Port 8002)..."
cd backend/utilisateurs
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
export DATABASE_URL="postgresql+psycopg://library_user:library_pass@localhost:5433/utilisateurs_db"
uvicorn app.main:app --reload --port 8002 &
UTILISATEURS_PID=$!
cd ../..

echo "🔄 Lancement du Service Emprunts (Port 8003)..."
cd backend/emprunts
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
export DATABASE_URL="postgresql+psycopg://library_user:library_pass@localhost:5433/emprunts_db"
export LIVRES_SERVICE_URL="http://localhost:8001"
export UTILISATEURS_SERVICE_URL="http://localhost:8002"
uvicorn app.main:app --reload --port 8003 &
EMPRUNTS_PID=$!
cd ../..

echo "🤖 Lancement du Service Recommandation (Port 8004)..."
cd backend/recommandation
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
export DATABASE_URL="postgresql+psycopg://library_user:library_pass@localhost:5433/recommandation_db"
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

# Fonction pour fermer tous les services proprement en quittant
cleanup() {
    echo ""
    echo "🛑 Arrêt de tous les services en cours..."
    kill $LIVRES_PID $UTILISATEURS_PID $EMPRUNTS_PID $RECO_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Capture le signal CTRL+C
trap cleanup SIGINT SIGTERM

# Empêche le script de se fermer
wait
