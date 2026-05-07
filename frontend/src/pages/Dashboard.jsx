import React, { useState, useEffect } from 'react';
import './Dashboard.css';
import { empruntsService } from '../services/empruntsService';
import { livresService } from '../services/livresService';
import { authService } from '../services/authService';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const [emprunts, setEmprunts] = useState([]);
  const [books, setBooks] = useState({});
  const [users, setUsers] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  const currentUser = authService.getCurrentUser();
  const isPersonnel = currentUser?.type_utilisateur === 'PERSONNEL' || currentUser?.type_utilisateur === 'ADMIN';

  useEffect(() => {
    if (!currentUser) {
      navigate('/login');
      return;
    }
    if (!isPersonnel) {
      toast.error("Accès refusé. Réservé au personnel.");
      navigate('/');
      return;
    }

    fetchDashboardData();
  }, [currentUser?.id_utilisateur, isPersonnel, navigate]);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    try {
      // 1. Charger tous les emprunts
      const empruntsData = await empruntsService.getEmprunts();
      setEmprunts(empruntsData);

      // 2. Charger tous les livres pour le mapping (optimisable mais ok ici)
      const booksList = await livresService.getLivres();
      const booksMap = {};
      booksList.forEach(b => booksMap[b.id] = b);
      setBooks(booksMap);

      // 3. Charger tous les utilisateurs pour le mapping
      // Note: On suppose qu'il y a un endpoint /utilisateurs/ (accessible au personnel)
      const response = await fetch('http://localhost:8002/utilisateurs/');
      if (response.ok) {
        const usersList = await response.json();
        const usersMap = {};
        usersList.forEach(u => usersMap[u.id_utilisateur] = u);
        setUsers(usersMap);
      }
    } catch (error) {
      console.error("Erreur de chargement du dashboard", error);
      toast.error("Erreur lors du chargement des données.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleMarquerRetour = async (empruntId) => {
    try {
      await empruntsService.retournerLivre(empruntId);
      toast.success("Livre marqué comme retourné !");
      fetchDashboardData();
    } catch (error) {
      toast.error(error.message);
    }
  };

  if (isLoading) return (
    <div className="loader-container">
      <div className="spinner"></div>
      <p className="loading-text">Chargement du dashboard...</p>
    </div>
  );

  return (
    <div className="dashboard-container">
      <div className="dashboard-header animate-fade-in">
        <h1 className="dashboard-title">Tableau de <span className="text-gradient">Bord</span></h1>
        <p className="dashboard-subtitle">Gestion globale des emprunts et retours.</p>
      </div>

      <div className="dashboard-stats grid">
        <div className="stat-card glass-panel">
          <span className="stat-value">{emprunts.length}</span>
          <span className="stat-label">Total Emprunts</span>
        </div>
        <div className="stat-card glass-panel">
          <span className="stat-value">{emprunts.filter(e => !e.date_retour_effective).length}</span>
          <span className="stat-label">En Cours</span>
        </div>
        <div className="stat-card glass-panel">
          <span className="stat-value">{emprunts.filter(e => e.en_retard && !e.date_retour_effective).length}</span>
          <span className="stat-label" style={{color: '#ef4444'}}>En Retard</span>
        </div>
      </div>

      <div className="dashboard-table-container glass-panel animate-fade-in">
        <table className="dashboard-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Utilisateur</th>
              <th>Livre</th>
              <th>Retour Prévu</th>
              <th>Statut</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {emprunts.map(e => (
              <tr key={e.id}>
                <td>{new Date(e.date_emprunt).toLocaleDateString()}</td>
                <td>
                  <div className="user-info">
                    <strong>{users[e.utilisateur_id]?.nom_prenom || 'Inconnu'}</strong>
                    <span className="user-email">{users[e.utilisateur_id]?.email || e.utilisateur_id.substring(0, 8)}</span>
                  </div>
                </td>
                <td>
                  <div className="book-info-dash">
                    <strong>{books[e.livre_id]?.titre || `Livre #${e.livre_id}`}</strong>
                    <span className="book-isbn-dash">{books[e.livre_id]?.isbn || '-'}</span>
                  </div>
                </td>
                <td>{new Date(e.date_retour_prevue).toLocaleDateString()}</td>
                <td>
                  {e.date_retour_effective ? (
                    <span className="badge badge-success">Retourné</span>
                  ) : (
                    <span className={`badge ${e.en_retard ? 'badge-danger' : 'badge-warning'}`}>
                      {e.en_retard ? 'En Retard' : 'En Cours'}
                    </span>
                  )}
                </td>
                <td>
                  {!e.date_retour_effective && (
                    <button 
                      className="btn btn-primary btn-sm"
                      onClick={() => handleMarquerRetour(e.id)}
                    >
                      Retourner
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {emprunts.length === 0 && (
          <div className="empty-table">Aucun emprunt enregistré.</div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
