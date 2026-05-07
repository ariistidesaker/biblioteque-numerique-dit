import React, { useState, useEffect } from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import './Navbar.css';

const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);
  const navigate = useNavigate();

  // On récupère l'utilisateur connecté
  const user = authService.getCurrentUser();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLogout = () => {
    authService.logout();
    navigate('/');
  };

  return (
    <header className={`navbar ${scrolled ? 'scrolled glass-panel' : ''}`}>
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <span className="logo-icon">📚</span>
          <span className="logo-text">Biblio<span className="highlight">Tech</span></span>
        </Link>

        <nav className="navbar-links">
          <NavLink to="/" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            Accueil
          </NavLink>
          <NavLink to="/catalogue" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            Catalogue
          </NavLink>
          {user && (
            <NavLink to="/profil" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              Mon Profil
            </NavLink>
          )}
        </nav>

        <div className="navbar-actions" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {user ? (
            <>
              <span style={{ fontSize: '0.9rem', color: 'var(--text)', fontWeight: '600' }}>
                👤 {user.nom_prenom || 'Utilisateur'}
              </span>
              <button onClick={handleLogout} className="btn btn-outline btn-sm" style={{ padding: '0.4rem 1rem' }}>Déconnexion</button>
            </>
          ) : (
            <Link to="/login" className="btn btn-primary btn-sm">Se Connecter</Link>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
