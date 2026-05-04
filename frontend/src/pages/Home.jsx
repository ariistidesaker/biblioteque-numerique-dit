import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

const Home = () => {
  return (
    <div className="home-container">
      {/* Hero Section */}
      <section className="hero-section animate-fade-in">
        <div className="hero-content">
          <div className="badge glass-panel">✨ Nouvelle plateforme DIT</div>
          <h1 className="hero-title">
            Explorez le savoir avec <br/>
            <span className="text-gradient">BiblioTech</span>
          </h1>
          <p className="hero-subtitle">
            Une bibliothèque numérique moderne, rapide et intelligente.
            Empruntez des livres, découvrez des recommandations personnalisées et enrichissez vos connaissances.
          </p>
          <div className="hero-actions">
            <Link to="/catalogue" className="btn btn-primary btn-lg">
              Parcourir le Catalogue
            </Link>
            <Link to="/profil" className="btn btn-outline btn-lg">
              Mon Espace
            </Link>
          </div>
        </div>
        
        {/* Abstract 3D/Glass decoration */}
        <div className="hero-visual">
          <div className="glass-card card-1">
            <div className="card-icon">📚</div>
            <div className="card-text">+10k Livres</div>
          </div>
          <div className="glass-card card-2">
            <div className="card-icon">🤖</div>
            <div className="card-text">IA Recommandation</div>
          </div>
          <div className="glass-card card-3">
            <div className="card-icon">⚡</div>
            <div className="card-text">Accès Immédiat</div>
          </div>
          <div className="blur-blob blob-primary"></div>
          <div className="blur-blob blob-secondary"></div>
        </div>
      </section>
    </div>
  );
};

export default Home;
