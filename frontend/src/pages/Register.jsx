import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Login.css'; // On réutilise les styles du Login pour une cohérence visuelle

const Register = () => {
  const [formData, setFormData] = useState({
    nom: '',
    email: '',
    password: '',
    confirmPassword: '',
    type: 'Etudiant'
  });
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.id]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulation d'une requête API
    setTimeout(() => {
      setIsLoading(false);
      navigate('/login');
    }, 1500);
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
                <option value="Etudiant">Étudiant</option>
                <option value="Professeur">Professeur</option>
                <option value="Personnel">Personnel</option>
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
