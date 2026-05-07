import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { authService } from '../services/authService';
import './Login.css';

const Confirmation = () => {
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const navigate = useNavigate();
  const location = useLocation();
  const email = location.state?.email; // Récupéré depuis la page Register

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) {
      setError("Email introuvable. Veuillez vous réinscrire.");
      return;
    }

    setIsLoading(true);
    setError('');
    
    try {
      await authService.confirmEmail(email, code);
      setSuccess("Compte activé ! Redirection vers la connexion...");
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      setError(err.message || 'Code invalide.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!email) {
    return (
      <div className="login-container">
        <div className="login-card glass-panel" style={{ textAlign: 'center' }}>
          <h2>Erreur</h2>
          <p>Aucun email trouvé. Veuillez repasser par la page d'inscription.</p>
          <button className="btn btn-primary" onClick={() => navigate('/inscription')} style={{ marginTop: '1rem' }}>S'inscrire</button>
        </div>
      </div>
    );
  }

  return (
    <div className="login-container">
      <div className="blur-blob blob-login-1"></div>
      <div className="blur-blob blob-login-2"></div>

      <div className="login-card glass-panel animate-fade-in">
        <div className="login-header">
          <div className="login-icon">✉️</div>
          <h2>Vérifiez vos emails</h2>
          <p>Nous avons envoyé un code de confirmation à <strong>{email}</strong>.</p>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>(Regardez dans la console de votre backend pour le voir)</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && (
            <div className="error-message" style={{ color: '#ef4444', backgroundColor: '#fef2f2', padding: '0.75rem', borderRadius: '8px', border: '1px solid #fca5a5' }}>
              {error}
            </div>
          )}
          {success && (
            <div className="success-message" style={{ color: '#10b981', backgroundColor: '#ecfdf5', padding: '0.75rem', borderRadius: '8px', border: '1px solid #6ee7b7' }}>
              {success}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="code">Code de confirmation (6 chiffres)</label>
            <div className="input-wrapper">
              <span className="input-icon">🔑</span>
              <input
                type="text"
                id="code"
                placeholder="123456"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                maxLength="6"
                required
              />
            </div>
          </div>

          <button 
            type="submit" 
            className={`btn btn-primary btn-full login-btn ${isLoading ? 'loading' : ''}`}
            disabled={isLoading || success}
          >
            {isLoading ? 'Vérification...' : 'Valider mon inscription'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Confirmation;
