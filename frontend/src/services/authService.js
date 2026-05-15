const API_URL = import.meta.env.VITE_UTILISATEURS_API_URL || 'http://localhost:8002';

export const authService = {
  /**
   * Connecte un utilisateur
   * @param {string} email 
   * @param {string} password 
   * @returns {Promise<Object>} Les données de l'utilisateur
   */
  async login(email, password) {
    try {
      const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, mot_de_passe: password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Erreur lors de la connexion');
      }

      // Sauvegarde de l'utilisateur dans le stockage local
      localStorage.setItem('user', JSON.stringify(data));
      return data;
    } catch (error) {
      console.error('Erreur login:', error);
      throw error;
    }
  },

  /**
   * Inscrit un nouvel utilisateur
   * @param {Object} userData 
   * @returns {Promise<Object>}
   */
  async register(userData) {
    try {
      const response = await fetch(`${API_URL}/utilisateurs/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Erreur lors de l\'inscription');
      }

      return data;
    } catch (error) {
      console.error('Erreur register:', error);
      throw error;
    }
  },

  /**
   * Confirme l'email avec un code
   * @param {string} email 
   * @param {string} code 
   * @returns {Promise<Object>}
   */
  async confirmEmail(email, code) {
    try {
      const response = await fetch(`${API_URL}/confirmer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, code }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Erreur lors de la confirmation');
      }

      return data;
    } catch (error) {
      console.error('Erreur confirm:', error);
      throw error;
    }
  },

  /**
   * Demande de réinitialisation de mot de passe
   * @param {string} email 
   * @returns {Promise<Object>}
   */
  async forgotPassword(email) {
    try {
      const response = await fetch(`${API_URL}/mot-de-passe-oublie`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Erreur lors de la demande de réinitialisation');
      }

      return data;
    } catch (error) {
      console.error('Erreur forgotPassword:', error);
      throw error;
    }
  },

  /**
   * Applique le nouveau mot de passe
   * @param {string} token 
   * @param {string} newPassword 
   * @returns {Promise<Object>}
   */
  async resetPassword(token, newPassword) {
    try {
      const response = await fetch(`${API_URL}/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token, nouveau_mot_de_passe: newPassword }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Erreur lors de la réinitialisation');
      }

      return data;
    } catch (error) {
      console.error('Erreur resetPassword:', error);
      throw error;
    }
  },

  /**
   * Récupère le profil complet d'un utilisateur par son ID
   * @param {string} userId 
   * @returns {Promise<Object>}
   */
  async getUserProfile(userId) {
    try {
      const response = await fetch(`${API_URL}/utilisateurs/${userId}`);
      if (!response.ok) {
        throw new Error('Erreur lors de la récupération du profil');
      }
      return await response.json();
    } catch (error) {
      console.error('Erreur getUserProfile:', error);
      throw error;
    }
  },

  /**
   * Met à jour le profil utilisateur
   * @param {string} userId 
   * @param {Object} updateData 
   * @returns {Promise<Object>}
   */
  async updateUser(userId, updateData) {
    try {
      const response = await fetch(`${API_URL}/utilisateurs/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Erreur lors de la mise à jour du profil');
      }

      // Mettre à jour les infos dans le localStorage si c'est l'utilisateur connecté
      const currentUser = this.getCurrentUser();
      if (currentUser && currentUser.id_utilisateur === userId) {
        localStorage.setItem('user', JSON.stringify({ ...currentUser, ...data }));
      }

      return data;
    } catch (error) {
      console.error('Erreur updateUser:', error);
      throw error;
    }
  },

  /**
   * Déconnecte l'utilisateur
   */
  logout() {
    localStorage.removeItem('user');
  },

  /**
   * Récupère l'utilisateur connecté
   * @returns {Object|null}
   */
  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }
};
