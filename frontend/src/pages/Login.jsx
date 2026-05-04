import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Login.css';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulation d'une requête API
    setTimeout(() => {
      setIsLoading(false);
      // Redirection après connexion simulée
      navigate('/catalogue');
    }, 1500);
  };

  return (
    <div className="login-container">
      {/* Background decorations */}
      <div className="blur-blob blob-login-1"></div>
      <div className="blur-blob blob-login-2"></div>

      <div className="login-card glass-panel animate-fade-in">
        <div className="login-header">
          <div className="login-icon">🔐</div>
          <h2>Bon retour !</h2>
          <p>Connectez-vous pour accéder à votre espace BiblioTech.</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Adresse Email</label>
            <div className="input-wrapper">
              <span className="input-icon">✉️</span>
              <input
                type="email"
                id="email"
                placeholder="votre@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <div className="label-row">
              <label htmlFor="password">Mot de passe</label>
              <Link to="/mot-de-passe-oublie" className="forgot-password">Mot de passe oublié ?</Link>
            </div>
            <div className="input-wrapper">
              <span className="input-icon">🔑</span>
              <input
                type="password"
                id="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <button 
            type="submit" 
            className={`btn btn-primary btn-full login-btn ${isLoading ? 'loading' : ''}`}
            disabled={isLoading}
          >
            {isLoading ? 'Connexion en cours...' : 'Se Connecter'}
          </button>
        </form>

        <div className="login-footer">
          <p>Pas encore de compte ? <Link to="/inscription" className="register-link">S'inscrire</Link></p>
        </div>
      </div>
    </div>
  );
};

export default Login;
