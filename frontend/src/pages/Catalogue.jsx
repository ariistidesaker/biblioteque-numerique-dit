import React, { useState, useEffect } from 'react';
import './Catalogue.css';
import { livresService } from '../services/livresService';
import { authService } from '../services/authService';
import { empruntsService } from '../services/empruntsService';
import toast from 'react-hot-toast';

const Catalogue = () => {
  const [books, setBooks] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState('add'); // 'add' or 'edit'
  const [currentBook, setCurrentBook] = useState({ 
    titre: '', 
    auteur: '', 
    isbn: '', 
    description: '',
    exemplaires_totaux: 1
  });

  const currentUser = authService.getCurrentUser();
  const isPersonnel = currentUser?.type_utilisateur === 'PERSONNEL' || currentUser?.type_utilisateur === 'ADMIN';

  useEffect(() => {
    fetchBooks();
  }, []);

  const fetchBooks = async () => {
    setIsLoading(true);
    try {
      const data = await livresService.getLivres();
      setBooks(data);
    } catch (error) {
      console.error("Erreur de chargement", error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredBooks = books.filter(book => {
    return book.titre.toLowerCase().includes(searchTerm.toLowerCase()) || 
           book.auteur.toLowerCase().includes(searchTerm.toLowerCase()) ||
           (book.isbn && book.isbn.includes(searchTerm));
  });

  const handleOpenModal = (mode, book = { titre: '', auteur: '', isbn: '', description: '', exemplaires_totaux: 1 }) => {
    setModalMode(mode);
    setCurrentBook(book);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setCurrentBook({ 
      titre: '', 
      auteur: '', 
      isbn: '', 
      description: '',
      exemplaires_totaux: 1
    });
  };

  const handleSaveBook = async (e) => {
    e.preventDefault();
    try {
      if (modalMode === 'add') {
        await livresService.createLivre(currentBook);
        toast.success("Livre ajouté avec succès !");
      } else {
        await livresService.updateLivre(currentBook.id, currentBook);
        toast.success("Livre modifié avec succès !");
      }
      handleCloseModal();
      fetchBooks();
    } catch (error) {
      toast.error("Erreur: " + error.message);
    }
  };

  const handleDeleteBook = async (id) => {
    if (window.confirm("Êtes-vous sûr de vouloir supprimer ce livre ?")) {
      try {
        await livresService.deleteLivre(id);
        toast.success("Livre supprimé !");
        fetchBooks();
      } catch (error) {
        toast.error("Erreur lors de la suppression: " + error.message);
      }
    }
  };

  const handleEmprunter = async (livreId) => {
    if (!currentUser) {
      toast.error("Vous devez être connecté pour emprunter un livre.");
      return;
    }
    try {
      const dateRetourPrevue = new Date();
      dateRetourPrevue.setDate(dateRetourPrevue.getDate() + 14); // Emprunt de 14 jours par défaut
      
      await empruntsService.createEmprunt({
        livre_id: livreId,
        utilisateur_id: currentUser.id_utilisateur,
        date_retour_prevue: dateRetourPrevue.toISOString()
      });
      toast.success("Livre emprunté avec succès ! 🎉");
      fetchBooks(); // Rafraîchir pour voir le nouveau statut de disponibilité
    } catch (error) {
      toast.error(error.message);
    }
  };

  return (
    <div className="catalogue-container">
      <div className="catalogue-header animate-fade-in">
        <h1 className="catalogue-title">Catalogue des <span className="text-gradient">Livres</span></h1>
        <p className="catalogue-subtitle">Découvrez et empruntez parmi des milliers d'ouvrages.</p>
        
        <div className="search-bar glass-panel">
          <span className="search-icon">🔍</span>
          <input 
            type="text" 
            placeholder="Rechercher par titre, auteur, ISBN..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        {isPersonnel && (
          <button className="btn btn-primary animate-fade-in" onClick={() => handleOpenModal('add')} style={{ marginBottom: '2rem' }}>
            + Ajouter un Livre
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="loading-state">Chargement des livres...</div>
      ) : (
        <div className="books-grid">
          {filteredBooks.map((book, index) => (
            <div 
              key={book.id} 
              className="book-card glass-panel animate-fade-in"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className={`book-cover ${!book.image_url ? `gradient-${(book.id % 6) + 1}` : ''}`} style={book.image_url ? { padding: 0, overflow: 'hidden' } : {}}>
                {book.image_url && <img src={book.image_url} alt={`Couverture de ${book.titre}`} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />}
                <div className={`status-badge ${book.disponible ? 'available' : 'unavailable'}`} style={book.image_url ? { position: 'absolute', top: '10px', right: '10px' } : {}}>
                  {book.disponible ? `${book.exemplaires_totaux} exemplaires` : 'Indisponible'}
                </div>
              </div>
              
              <div className="book-info">
                <span className="book-category">Livre</span>
                <h3 className="book-title">{book.titre}</h3>
                <p className="book-author">{book.auteur}</p>
                <p className="book-isbn" style={{fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem'}}>ISBN: {book.isbn}</p>
                
                <div className="book-actions">
                  {!isPersonnel && (
                    <button 
                      className={`btn ${book.disponible ? 'btn-primary' : 'btn-disabled'} btn-full`}
                      onClick={() => book.disponible && handleEmprunter(book.id)}
                      disabled={!book.disponible}
                    >
                      {book.disponible ? 'Emprunter' : 'Épuisé'}
                    </button>
                  )}
                  {isPersonnel && (
                    <div className="admin-actions" style={{display: 'flex', gap: '0.5rem', marginTop: '0.5rem', width: '100%'}}>
                      <button className="btn btn-outline btn-full" onClick={() => handleOpenModal('edit', book)}>Modifier</button>
                      <button className="btn btn-outline btn-full" style={{borderColor: '#ef4444', color: '#ef4444'}} onClick={() => handleDeleteBook(book.id)}>Supprimer</button>
                    </div>
                  )}
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
      )}

      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content glass-panel animate-fade-in">
            <h2>{modalMode === 'add' ? 'Ajouter un Livre' : 'Modifier le Livre'}</h2>
            <form onSubmit={handleSaveBook} className="modal-form">
              <div className="form-group">
                <label>Titre</label>
                <input required type="text" value={currentBook.titre} onChange={e => setCurrentBook({...currentBook, titre: e.target.value})} className="form-input" />
              </div>
              <div className="form-group">
                <label>Auteur</label>
                <input required type="text" value={currentBook.auteur} onChange={e => setCurrentBook({...currentBook, auteur: e.target.value})} className="form-input" />
              </div>
              <div className="form-group">
                <label>ISBN</label>
                <input required type="text" value={currentBook.isbn} onChange={e => setCurrentBook({...currentBook, isbn: e.target.value})} className="form-input" />
              </div>
              <div className="form-group">
                <label>URL de l'image</label>
                <input type="url" placeholder="https://..." value={currentBook.image_url || ''} onChange={e => setCurrentBook({...currentBook, image_url: e.target.value})} className="form-input" />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea rows="4" value={currentBook.description || ''} onChange={e => setCurrentBook({...currentBook, description: e.target.value})} className="form-input"></textarea>
              </div>
              <div className="form-group">
                <label>Exemplaires Totaux</label>
                <input type="number" min="0" value={currentBook.exemplaires_totaux || 1} onChange={e => setCurrentBook({...currentBook, exemplaires_totaux: parseInt(e.target.value) || 0})} className="form-input" />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-outline" onClick={handleCloseModal}>Annuler</button>
                <button type="submit" className="btn btn-primary">Enregistrer</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Catalogue;
