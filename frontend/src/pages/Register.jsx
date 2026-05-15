import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import './Login.css'; // On réutilise les styles du Login pour une cohérence visuelle

const Register = () => {
  const [formData, setFormData] = useState({
    nom: '',
    email: '',
    password: '',
    confirmPassword: '',
    type: 'ETUDIANT'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.id]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      await authService.register({
        email: formData.email,
        mot_de_passe: formData.password,
        nom_prenom: formData.nom,
        type_utilisateur: formData.type
      });
      // Redirection vers la page de confirmation avec l'email
      navigate('/confirmation', { state: { email: formData.email } });
    } catch (err) {
      setError(err.message || 'Erreur lors de la création du compte.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="blur-blob blob-login-1"></div>
      <div className="blur-blob blob-login-2"></div>

      <div className="login-card glass-panel animate-fade-in" style={{ maxWidth: '500px' }}>
        <div className="login-header">
          <div className="login-icon">🎓</div>
          <h2>Créer un compte</h2>
          <p>Rejoignez la communauté BiblioTech dès aujourd'hui.</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && (
            <div className="error-message" style={{ color: '#ef4444', backgroundColor: '#fef2f2', padding: '0.75rem', borderRadius: '8px', fontSize: '0.9rem', border: '1px solid #fca5a5' }}>
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="nom">Nom complet</label>
            <div className="input-wrapper">
              <span className="input-icon">👤</span>
              <input
                type="text"
                id="nom"
                placeholder="Jean Dupont"
                value={formData.nom}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="email">Adresse Email</label>
            <div className="input-wrapper">
              <span className="input-icon">✉️</span>
              <input
                type="email"
                id="email"
                placeholder="votre@email.com"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="type">Type d'utilisateur</label>
            <div className="input-wrapper">
              <span className="input-icon">🏷️</span>
              <select 
                id="type" 
                value={formData.type} 
                onChange={handleChange}
                className="custom-select"
                required
              >
                <option value="ETUDIANT">Étudiant</option>
                <option value="PROFESSEUR">Professeur</option>
                <option value="PERSONNEL">Personnel</option>
              </select>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label htmlFor="password">Mot de passe</label>
              <div className="input-wrapper">
                <span className="input-icon">🔑</span>
                <input
                  type="password"
                  id="password"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">Confirmation</label>
              <div className="input-wrapper">
                <span className="input-icon">🔒</span>
                <input
                  type="password"
                  id="confirmPassword"
                  placeholder="••••••••"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>
          </div>

          <button 
            type="submit" 
            className={`btn btn-primary btn-full login-btn ${isLoading ? 'loading' : ''}`}
            disabled={isLoading || formData.password !== formData.confirmPassword}
          >
            {isLoading ? 'Création en cours...' : 'S\'inscrire'}
          </button>
        </form>

        <div className="login-footer">
          <p>Déjà un compte ? <Link to="/login" className="register-link">Se connecter</Link></p>
        </div>
      </div>
    </div>
  );
};

export default Register;
