/**
 * recommandationService.js
 * Service d'appels vers le Service Recommandation (port 8004)
 */

const API_URL = import.meta.env.VITE_RECOMMANDATION_API_URL || 'http://localhost:8004';

export const recommandationService = {

  /**
   * Obtenir les recommandations personnalisées pour un utilisateur
   * @param {string} utilisateurId - UUID de l'utilisateur
   * @param {number} n - Nombre de recommandations (défaut: 5)
   * @returns {Promise<{utilisateur_id: string, livre_ids: number[], source: string}>}
   */
  async getRecommandations(utilisateurId, n = 5) {
    const response = await fetch(
      `${API_URL}/recommandations/${utilisateurId}?n=${n}`
    );
    if (!response.ok) {
      throw new Error('Erreur lors de la récupération des recommandations');
    }
    return response.json();
  },

  /**
   * Obtenir les livres les plus populaires (sans personnalisation)
   * @param {number} n - Nombre de livres (défaut: 5)
   * @returns {Promise<{livre_ids: number[], source: string}>}
   */
  async getPopulaires(n = 5) {
    const response = await fetch(`${API_URL}/recommandations/populaires?n=${n}`);
    if (!response.ok) {
      throw new Error('Erreur lors de la récupération des livres populaires');
    }
    return response.json();
  },

  /**
   * Déclencher un ré-entraînement du modèle (asynchrone)
   * @returns {Promise<{status: string, message: string}>}
   */
  async entrainerModele() {
    const response = await fetch(`${API_URL}/modele/entrainer`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error('Erreur lors du lancement de l\'entraînement');
    }
    return response.json();
  },

  /**
   * Obtenir les informations sur le modèle chargé
   * @returns {Promise<{model_loaded: boolean, n_users: number, n_books: number}>}
   */
  async getModelInfo() {
    const response = await fetch(`${API_URL}/modele/info`);
    if (!response.ok) {
      throw new Error('Erreur lors de la récupération des infos du modèle');
    }
    return response.json();
  },

  /**
   * Obtenir l'historique des entraînements
   * @param {number} limit
   * @returns {Promise<Array>}
   */
  async getHistoriqueEntrainement(limit = 10) {
    const response = await fetch(`${API_URL}/modele/historique?limit=${limit}`);
    if (!response.ok) {
      throw new Error('Erreur lors de la récupération de l\'historique');
    }
    return response.json();
  },

  /**
   * Vérifier la santé du service de recommandation
   * @returns {Promise<{status: string, model_loaded: boolean}>}
   */
  async getHealth() {
    const response = await fetch(`${API_URL}/health`);
    if (!response.ok) throw new Error('Service recommandation indisponible');
    return response.json();
  },
};
