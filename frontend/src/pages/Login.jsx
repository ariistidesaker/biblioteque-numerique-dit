import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import './Login.css';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      await authService.login(email, password);
      navigate('/catalogue'); // Redirection après connexion réussie
    } catch (err) {
      setError(err.message || 'Email ou mot de passe incorrect.');
    } finally {
      setIsLoading(false);
    }
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
          {error && (
            <div className="error-message" style={{ color: '#ef4444', backgroundColor: '#fef2f2', padding: '0.75rem', borderRadius: '8px', fontSize: '0.9rem', border: '1px solid #fca5a5' }}>
              {error}
            </div>
          )}

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
