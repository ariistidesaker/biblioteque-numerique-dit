const API_URL = 'http://localhost:8003'; // Port du service emprunts défini dans start-local.sh

export const empruntsService = {
  /**
   * Créer un nouvel emprunt
   * @param {Object} data { livre_id, utilisateur_id, date_retour_prevue }
   * @returns {Promise<Object>}
   */
  async createEmprunt(data) {
    const response = await fetch(`${API_URL}/emprunts/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || 'Erreur lors de l\'emprunt');
    return result;
  },

  /**
   * Retourner un livre
   * @param {number} empruntId 
   * @returns {Promise<Object>}
   */
  async retournerLivre(empruntId) {
    const response = await fetch(`${API_URL}/emprunts/${empruntId}/retour`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    });

    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || 'Erreur lors du retour du livre');
    return result;
  },

  /**
   * Lister l'historique des emprunts (avec filtres optionnels)
   * @param {Object} filters { utilisateur_id, livre_id, statut }
   * @returns {Promise<Array>}
   */
  async getEmprunts(filters = {}, skip = 0, limit = 100) {
    const queryParams = new URLSearchParams();
    if (filters.utilisateur_id) queryParams.append('utilisateur_id', filters.utilisateur_id);
    if (filters.livre_id) queryParams.append('livre_id', filters.livre_id);
    if (filters.statut) queryParams.append('statut', filters.statut);
    
    queryParams.append('skip', skip);
    queryParams.append('limit', limit);

    const url = `${API_URL}/emprunts/?${queryParams.toString()}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Erreur lors de la récupération des emprunts');
    return response.json();
  },

  /**
   * Lister les emprunts en retard
   * @returns {Promise<Array>}
   */
  async getRetards() {
    const response = await fetch(`${API_URL}/emprunts/retards`);
    if (!response.ok) throw new Error('Erreur lors de la récupération des retards');
    return response.json();
  },

  /**
   * Obtenir l'historique spécifique à un utilisateur
   * @param {string} utilisateurId 
   * @returns {Promise<Array>}
   */
  async getEmpruntsUtilisateur(utilisateurId) {
    const response = await fetch(`${API_URL}/emprunts/utilisateur/${utilisateurId}`);
    if (!response.ok) throw new Error('Erreur lors de la récupération de l\'historique utilisateur');
    return response.json();
  }
};
