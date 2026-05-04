import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Login.css'; // On réutilise les styles du Login

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSent, setIsSent] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulation d'une requête API d'envoi d'email
    setTimeout(() => {
      setIsLoading(false);
      setIsSent(true);
    }, 1500);
  };

  return (
    <div className="login-container">
      <div className="blur-blob blob-login-1"></div>
      <div className="blur-blob blob-login-2"></div>

      <div className="login-card glass-panel animate-fade-in">
        <div className="login-header">
          <div className="login-icon">🛡️</div>
          <h2>Mot de passe oublié</h2>
          <p>Entrez votre adresse email pour recevoir un lien de réinitialisation.</p>
        </div>

        {!isSent ? (
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

            <button 
              type="submit" 
              className={`btn btn-primary btn-full login-btn ${isLoading ? 'loading' : ''}`}
              disabled={isLoading}
            >
              {isLoading ? 'Envoi en cours...' : 'Envoyer le lien'}
            </button>
          </form>
        ) : (
          <div className="success-message" style={{ textAlign: 'center', padding: '1rem 0' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✅</div>
            <h3 style={{ marginBottom: '1rem', color: 'var(--text)' }}>Email envoyé !</h3>
            <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
              Si un compte est associé à <strong>{email}</strong>, vous recevrez un lien de réinitialisation dans quelques instants.
            </p>
          </div>
        )}

        <div className="login-footer">
          <p><Link to="/login" className="register-link" style={{ marginLeft: 0 }}>← Retour à la connexion</Link></p>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
