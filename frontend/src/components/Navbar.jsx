import React, { useState, useEffect } from 'react';
import { NavLink, Link } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

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
          <NavLink to="/profil" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            Mon Profil
          </NavLink>
        </nav>

        <div className="navbar-actions">
          <Link to="/login" className="btn btn-primary btn-sm">Se Connecter</Link>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
