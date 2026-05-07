import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import './Login.css'; // On réutilise les styles du Login
import { authService } from '../services/authService';

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const navigate = useNavigate();

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) {
      setError('Lien invalide ou expiré (aucun token fourni).');
    }
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      await authService.resetPassword(token, password);
      setIsSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err) {
      setError(err.message || 'Une erreur est survenue lors de la réinitialisation.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="blur-blob blob-login-1"></div>
      <div className="blur-blob blob-login-2"></div>

      <div className="login-card glass-panel animate-fade-in">
        <div className="login-header">
          <div className="login-icon">🔒</div>
          <h2>Nouveau mot de passe</h2>
          <p>Définissez votre nouveau mot de passe.</p>
        </div>

        {error && <div className="error-message" style={{ color: '#ef4444', backgroundColor: 'rgba(239, 68, 68, 0.1)', padding: '0.75rem', borderRadius: '8px', marginBottom: '1.5rem', textAlign: 'center', fontSize: '0.9rem', border: '1px solid rgba(239, 68, 68, 0.2)' }}>{error}</div>}

        {!isSuccess ? (
          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <label htmlFor="password">Nouveau mot de passe</label>
              <div className="input-wrapper">
                <span className="input-icon">🔑</span>
                <input
                  type="password"
                  id="password"
                  placeholder="Votre nouveau mot de passe"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  disabled={!token}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">Confirmer le mot de passe</label>
              <div className="input-wrapper">
                <span className="input-icon">🔑</span>
                <input
                  type="password"
                  id="confirmPassword"
                  placeholder="Confirmez le mot de passe"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  disabled={!token}
                />
              </div>
            </div>

            <button 
              type="submit" 
              className={`btn btn-primary btn-full login-btn ${isLoading ? 'loading' : ''}`}
              disabled={isLoading || !token}
            >
              {isLoading ? 'Enregistrement...' : 'Mettre à jour'}
            </button>
          </form>
        ) : (
          <div className="success-message" style={{ textAlign: 'center', padding: '1rem 0' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✅</div>
            <h3 style={{ marginBottom: '1rem', color: 'var(--text)' }}>Réinitialisé avec succès !</h3>
            <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
              Votre mot de passe a été mis à jour. Vous allez être redirigé vers la page de connexion...
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

export default ResetPassword;
