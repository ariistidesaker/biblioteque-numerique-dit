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
  
  // States pour la pagination et les filtres
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [hasMore, setHasMore] = useState(true);
  const [selectedStatut, setSelectedStatut] = useState("");
  const [searchTerm, setSearchTerm] = useState("");

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
  }, [currentUser?.id_utilisateur, isPersonnel, navigate, page, selectedStatut]);

  // Reset page when filter changes
  useEffect(() => {
    setPage(1);
  }, [selectedStatut]);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    try {
      // 1. Charger les emprunts paginés et filtrés par statut
      const skip = (page - 1) * limit;
      const filters = {};
      if (selectedStatut) filters.statut = selectedStatut;
      
      const empruntsData = await empruntsService.getEmprunts(filters, skip, limit);
      setEmprunts(empruntsData);
      setHasMore(empruntsData.length === limit);

      // 2. Charger les livres pour le mapping
      const booksList = await livresService.getLivres(0, 500);
      const booksMap = {};
      booksList.forEach(b => booksMap[b.id] = b);
      setBooks(booksMap);

      // 3. Charger tous les utilisateurs pour le mapping
      const usersUrl = import.meta.env.VITE_UTILISATEURS_API_URL || 'http://localhost:8002';
      const response = await fetch(`${usersUrl}/utilisateurs/`);
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

  const filteredEmprunts = emprunts.filter(e => {
    const user = users[e.utilisateur_id];
    const book = books[e.livre_id];
    
    const searchString = `${user?.nom_prenom || ''} ${book?.titre || ''}`.toLowerCase();
    return searchString.includes(searchTerm.toLowerCase());
  });

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
          <span className="stat-label">Emprunts (Page)</span>
        </div>
        <div className="stat-card glass-panel">
          <span className="stat-value">{emprunts.filter(e => !e.date_retour_effective).length}</span>
          <span className="stat-label">En Cours (Page)</span>
        </div>
        <div className="stat-card glass-panel">
          <span className="stat-value">{emprunts.filter(e => e.en_retard && !e.date_retour_effective).length}</span>
          <span className="stat-label" style={{color: '#ef4444'}}>En Retard (Page)</span>
        </div>
      </div>

      {/* Barre de Filtres */}
      <div className="dashboard-filters glass-panel animate-fade-in">
        <div className="search-box">
          <span>🔍</span>
          <input 
            type="text" 
            placeholder="Rechercher un utilisateur ou un livre..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="status-filter">
          <label>Statut:</label>
          <select value={selectedStatut} onChange={(e) => setSelectedStatut(e.target.value)}>
            <option value="">Tous les emprunts</option>
            <option value="en_cours">En Cours</option>
            <option value="retourne">Retournés</option>
            <option value="en_retard">En Retard</option>
          </select>
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
            {filteredEmprunts.map(e => (
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
                  {!e.date_retour_effective && currentUser?.type_utilisateur === 'PERSONNEL' && (
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
        {filteredEmprunts.length === 0 && (
          <div className="empty-table">Aucun emprunt ne correspond à vos filtres.</div>
        )}
      </div>

      <div className="pagination-controls animate-fade-in">
        <button 
          className={`btn btn-outline ${page === 1 ? 'btn-disabled' : ''}`}
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page === 1}
        >
          Précédent
        </button>
        <span className="page-info">Page <strong>{page}</strong></span>
        <button 
          className={`btn btn-outline ${!hasMore ? 'btn-disabled' : ''}`}
          onClick={() => setPage(p => p + 1)}
          disabled={!hasMore}
        >
          Suivant
        </button>
      </div>
    </div>
  );
};

export default Dashboard;
