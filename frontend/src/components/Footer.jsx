import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-grid">
          {/* Section Marque */}
          <div className="footer-brand">
            <Link to="/" className="footer-logo">
              <span className="logo-icon">📚</span>
              <span className="logo-text">Biblio<span className="highlight-white">Tech</span></span>
            </Link>
            <p className="footer-description">
              La plateforme numérique officielle du Dakar Institute of Technology pour l'emprunt et la consultation d'ouvrages académiques.
            </p>
          </div>

          {/* Section Liens Rapides */}
          <div className="footer-links-group">
            <h4 className="footer-title">Navigation</h4>
            <ul className="footer-links">
              <li><Link to="/">Accueil</Link></li>
              <li><Link to="/catalogue">Catalogue</Link></li>
              <li><Link to="/profil">Mon Profil</Link></li>
            </ul>
          </div>

          {/* Section Utilitaires */}
          <div className="footer-links-group">
            <h4 className="footer-title">Accès</h4>
            <ul className="footer-links">
              <li><Link to="/login">Se connecter</Link></li>
              <li><Link to="/inscription">S'inscrire</Link></li>
              <li><Link to="/mot-de-passe-oublie">Mot de passe oublié</Link></li>
            </ul>
          </div>

          {/* Section Contact */}
          <div className="footer-links-group">
            <h4 className="footer-title">Contact</h4>
            <ul className="footer-contact">
              <li>📍 Dakar, Sénégal</li>
              <li>✉️ contact@dit.sn</li>
              <li>🌐 dit.sn</li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <p>&copy; {currentYear} Dakar Institute of Technology. Tous droits réservés.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
