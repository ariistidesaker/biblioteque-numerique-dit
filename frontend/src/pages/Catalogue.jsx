import React, { useState } from 'react';
import './Catalogue.css';

// Mock data (en attendant de connecter l'API Livres)
const mockBooks = [
  { id: 1, titre: "L'Art de la Guerre", auteur: "Sun Tzu", categorie: "Stratégie", annee: 2020, dispo: true, cover: "gradient-1" },
  { id: 2, titre: "Clean Code", auteur: "Robert C. Martin", categorie: "Programmation", annee: 2008, dispo: false, cover: "gradient-2" },
  { id: 3, titre: "Sapiens", auteur: "Yuval Noah Harari", categorie: "Histoire", annee: 2011, dispo: true, cover: "gradient-3" },
  { id: 4, titre: "Design Patterns", auteur: "Gang of Four", categorie: "Programmation", annee: 1994, dispo: true, cover: "gradient-4" },
  { id: 5, titre: "Le Prince", auteur: "Nicolas Machiavel", categorie: "Philosophie", annee: 1532, dispo: true, cover: "gradient-5" },
  { id: 6, titre: "Introduction to Algorithms", auteur: "Thomas H. Cormen", categorie: "Programmation", annee: 2009, dispo: false, cover: "gradient-6" },
];

const categories = ["Tous", "Programmation", "Histoire", "Stratégie", "Philosophie"];

const Catalogue = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [activeCategory, setActiveCategory] = useState("Tous");

  const filteredBooks = mockBooks.filter(book => {
    const matchesSearch = book.titre.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          book.auteur.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCat = activeCategory === "Tous" || book.categorie === activeCategory;
    return matchesSearch && matchesCat;
  });

  return (
    <div className="catalogue-container">
      <div className="catalogue-header animate-fade-in">
        <h1 className="catalogue-title">Catalogue des <span className="text-gradient">Livres</span></h1>
        <p className="catalogue-subtitle">Découvrez et empruntez parmi des milliers d'ouvrages.</p>
        
        <div className="search-bar glass-panel">
          <span className="search-icon">🔍</span>
          <input 
            type="text" 
            placeholder="Rechercher par titre, auteur..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="categories-filter">
          {categories.map(cat => (
            <button 
              key={cat} 
              className={`filter-btn ${activeCategory === cat ? 'active' : ''}`}
              onClick={() => setActiveCategory(cat)}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      <div className="books-grid">
        {filteredBooks.map((book, index) => (
          <div 
            key={book.id} 
            className="book-card glass-panel animate-fade-in"
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            <div className={`book-cover ${book.cover}`}>
              {!book.dispo && <div className="status-badge unavailable">Indisponible</div>}
              {book.dispo && <div className="status-badge available">Disponible</div>}
            </div>
            
            <div className="book-info">
              <span className="book-category">{book.categorie}</span>
              <h3 className="book-title">{book.titre}</h3>
              <p className="book-author">{book.auteur} • {book.annee}</p>
              
              <div className="book-actions">
                <button 
                  className={`btn ${book.dispo ? 'btn-primary' : 'btn-outline'} btn-full`}
                  disabled={!book.dispo}
                >
                  {book.dispo ? 'Emprunter' : 'Sur Liste d\'Attente'}
                </button>
              </div>
            </div>
          </div>
        ))}
        {filteredBooks.length === 0 && (
          <div className="no-results">
            <p>Aucun livre ne correspond à votre recherche. 😔</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Catalogue;
