const API_URL = 'http://localhost:8001'; // Port du service livres défini dans docker-compose.yml

export const livresService = {
  /**
   * Récupère tous les livres
   * @param {number} skip 
   * @param {number} limit 
   * @returns {Promise<Array>}
   */
  async getLivres(skip = 0, limit = 100) {
    try {
      const response = await fetch(`${API_URL}/livres/?skip=${skip}&limit=${limit}`);
      if (!response.ok) throw new Error('Erreur lors de la récupération des livres');
      return await response.json();
    } catch (error) {
      console.error('Erreur getLivres:', error);
      throw error;
    }
  },

  /**
   * Recherche des livres
   * @param {Object} params - { titre, auteur, isbn }
   * @returns {Promise<Array>}
   */
  async searchLivres(params = {}) {
    try {
      const queryParams = new URLSearchParams();
      if (params.titre) queryParams.append('titre', params.titre);
      if (params.auteur) queryParams.append('auteur', params.auteur);
      if (params.isbn) queryParams.append('isbn', params.isbn);

      const response = await fetch(`${API_URL}/livres/recherche?${queryParams.toString()}`);
      if (!response.ok) throw new Error('Erreur lors de la recherche des livres');
      return await response.json();
    } catch (error) {
      console.error('Erreur searchLivres:', error);
      throw error;
    }
  },

  /**
   * Récupère un livre par son ID
   * @param {number} id 
   * @returns {Promise<Object>}
   */
  async getLivre(id) {
    try {
      const response = await fetch(`${API_URL}/livres/${id}`);
      if (!response.ok) throw new Error('Erreur lors de la récupération du livre');
      return await response.json();
    } catch (error) {
      console.error('Erreur getLivre:', error);
      throw error;
    }
  },

  /**
   * Ajoute un nouveau livre (Réservé au Personnel)
   * @param {Object} livreData 
   * @returns {Promise<Object>}
   */
  async createLivre(livreData) {
    try {
      const response = await fetch(`${API_URL}/livres/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(livreData),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Erreur lors de l\'ajout du livre');
      return data;
    } catch (error) {
      console.error('Erreur createLivre:', error);
      throw error;
    }
  },

  /**
   * Modifie un livre existant (Réservé au Personnel)
   * @param {number} id 
   * @param {Object} livreData 
   * @returns {Promise<Object>}
   */
  async updateLivre(id, livreData) {
    try {
      const response = await fetch(`${API_URL}/livres/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(livreData),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Erreur lors de la modification du livre');
      return data;
    } catch (error) {
      console.error('Erreur updateLivre:', error);
      throw error;
    }
  },

  /**
   * Supprime un livre (Réservé au Personnel)
   * @param {number} id 
   * @returns {Promise<void>}
   */
  async deleteLivre(id) {
    try {
      const response = await fetch(`${API_URL}/livres/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        let errorMsg = 'Erreur lors de la suppression du livre';
        try {
          const data = await response.json();
          errorMsg = data.detail || errorMsg;
        } catch(e) {}
        throw new Error(errorMsg);
      }
    } catch (error) {
      console.error('Erreur deleteLivre:', error);
      throw error;
    }
  }
};
