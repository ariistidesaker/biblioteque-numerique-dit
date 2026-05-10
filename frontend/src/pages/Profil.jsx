import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../services/authService';
import { empruntsService } from '../services/empruntsService';
import { livresService } from '../services/livresService';
import { recommandationService } from '../services/recommandationService';
import toast from 'react-hot-toast';
import './Profil.css';

const Profil = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [profileData, setProfileData] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [saveLoading, setSaveLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // Emprunts state
  const [emprunts, setEmprunts] = useState([]);
  const [livres, setLivres] = useState({});

  // Recommandations state
  const [recommandations, setRecommandations] = useState([]);
  const [recoLivres, setRecoLivres] = useState([]);
  const [recoLoading, setRecoLoading] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    nom_prenom: '',
    numero_telephone: '',
    // Etudiant
    numero_etudiant: '',
    filiere: '',
    niveau: '',
    // Professeur / Personnel
    specialite: '',
    poste: '',
    departement: ''
  });

  useEffect(() => {
    const currentUser = authService.getCurrentUser();
    if (!currentUser) {
      navigate('/login');
      return;
    }
    setUser(currentUser);
    fetchProfile(currentUser.id_utilisateur);
  }, [navigate]);

  const fetchProfile = async (userId) => {
    try {
      setIsLoading(true);
      const data = await authService.getUserProfile(userId);
      setProfileData(data);
      
      // Charger les emprunts et les recommandations
      try {
        const [userEmprunts, allLivres] = await Promise.all([
          empruntsService.getEmpruntsUtilisateur(userId),
          livresService.getLivres()
        ]);
        
        setEmprunts(userEmprunts);
        
        // Créer un dictionnaire de livres pour un accès facile
        const livresDict = {};
        allLivres.forEach(livre => {
          livresDict[livre.id] = livre;
        });
        setLivres(livresDict);

        // Charger les recommandations personnalisées
        try {
          setRecoLoading(true);
          const recoData = await recommandationService.getRecommandations(userId, 5);
          const recoIds = recoData.livre_ids || [];
          // Récupérer les détails des livres recommandés
          const recoDetails = recoIds
            .map(id => livresDict[id])
            .filter(Boolean);
          setRecommandations(recoIds);
          setRecoLivres(recoDetails);
        } catch (recoErr) {
          console.warn("Service de recommandation indisponible:", recoErr);
        } finally {
          setRecoLoading(false);
        }
      } catch (empruntErr) {
        console.error("Erreur lors du chargement des emprunts:", empruntErr);
      }

      // Init form data
      const newFormData = {
        nom_prenom: data.nom_prenom || '',
        numero_telephone: data.numero_telephone || '',
        numero_etudiant: data.etudiant?.numero_etudiant || '',
        filiere: data.etudiant?.filiere || '',
        niveau: data.etudiant?.niveau || '',
        specialite: data.professeur?.specialite || '',
        poste: data.personnel?.poste || '',
        departement: data.professeur?.departement || data.personnel?.departement || ''
      };
      setFormData(newFormData);
    } catch (err) {
      setError('Impossible de charger les données du profil.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setSaveLoading(true);

    try {
      const updatePayload = {
        nom_prenom: formData.nom_prenom,
        numero_telephone: formData.numero_telephone
      };

      if (profileData.type_utilisateur === 'etudiant') {
        updatePayload.profil_etudiant = {
          numero_etudiant: formData.numero_etudiant,
          filiere: formData.filiere,
          niveau: formData.niveau
        };
      } else if (profileData.type_utilisateur === 'professeur') {
        updatePayload.profil_professeur = {
          specialite: formData.specialite,
          departement: formData.departement
        };
      } else if (profileData.type_utilisateur === 'personnel') {
        updatePayload.profil_personnel = {
          poste: formData.poste,
          departement: formData.departement
        };
      }

      const updatedData = await authService.updateUser(user.id_utilisateur, updatePayload);
      setProfileData(updatedData);
      setIsEditing(false);
      toast.success('Profil mis à jour avec succès !');
      
      // Rafraîchir l'affichage du nom dans la navbar si besoin
      setUser(authService.getCurrentUser());
    } catch (err) {
      toast.error(err.message || 'Erreur lors de la mise à jour.');
    } finally {
      setSaveLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="loader-container">
        <div className="spinner"></div>
        <p className="loading-text">Chargement de votre profil...</p>
      </div>
    );
  }

  if (!profileData) {
    return <div className="profil-container"><div className="error-message">{error}</div></div>;
  }

  const roleColors = {
    etudiant: 'var(--primary)',
    professeur: 'var(--secondary)',
    personnel: '#eab308',
    admin: '#ef4444'
  };
  const roleColor = roleColors[profileData.type_utilisateur] || 'var(--primary)';

  return (
    <div className="profil-container animate-fade-in">
      <div className="profil-header" style={{ borderBottomColor: roleColor }}>
        <div className="profil-avatar" style={{ backgroundColor: roleColor }}>
          {profileData.nom_prenom.charAt(0).toUpperCase()}
        </div>
        <div className="profil-title-area">
          <h1>{profileData.nom_prenom}</h1>
          <span className="role-badge" style={{ backgroundColor: roleColor }}>
            {profileData.type_utilisateur.toUpperCase()}
          </span>
        </div>
      </div>

      <div className="profil-content">
        {message && <div className="success-message" style={{ marginBottom: '1.5rem', padding: '1rem', backgroundColor: 'rgba(34, 197, 94, 0.1)', color: '#22c55e', borderRadius: '8px' }}>{message}</div>}
        {error && <div className="error-message" style={{ marginBottom: '1.5rem' }}>{error}</div>}

        {!isEditing ? (
          <div className="profil-details card glass-panel">
            <div className="detail-group">
              <span className="detail-label">Email</span>
              <span className="detail-value">{profileData.email}</span>
            </div>
            <div className="detail-group">
              <span className="detail-label">Téléphone</span>
              <span className="detail-value">{profileData.numero_telephone || 'Non renseigné'}</span>
            </div>
            <div className="detail-group">
              <span className="detail-label">Statut du compte</span>
              <span className="detail-value">
                {profileData.status === 'actif' ? '✅ Actif' : (profileData.status === 'en_attente' ? '⏳ En attente' : '❌ Inactif')}
              </span>
            </div>

            {profileData.type_utilisateur === 'etudiant' && profileData.etudiant && (
              <>
                <div className="detail-divider"></div>
                <h3>Informations Étudiant</h3>
                <div className="detail-group">
                  <span className="detail-label">Numéro Étudiant</span>
                  <span className="detail-value">{profileData.etudiant.numero_etudiant || '-'}</span>
                </div>
                <div className="detail-group">
                  <span className="detail-label">Filière</span>
                  <span className="detail-value">{profileData.etudiant.filiere || '-'}</span>
                </div>
                <div className="detail-group">
                  <span className="detail-label">Niveau</span>
                  <span className="detail-value">{profileData.etudiant.niveau || '-'}</span>
                </div>
              </>
            )}

            {profileData.type_utilisateur === 'professeur' && profileData.professeur && (
              <>
                <div className="detail-divider"></div>
                <h3>Informations Professeur</h3>
                <div className="detail-group">
                  <span className="detail-label">Spécialité</span>
                  <span className="detail-value">{profileData.professeur.specialite || '-'}</span>
                </div>
                <div className="detail-group">
                  <span className="detail-label">Département</span>
                  <span className="detail-value">{profileData.professeur.departement || '-'}</span>
                </div>
              </>
            )}

            {profileData.type_utilisateur === 'personnel' && profileData.personnel && (
              <>
                <div className="detail-divider"></div>
                <h3>Informations Personnel</h3>
                <div className="detail-group">
                  <span className="detail-label">Poste</span>
                  <span className="detail-value">{profileData.personnel.poste || '-'}</span>
                </div>
                <div className="detail-group">
                  <span className="detail-label">Département</span>
                  <span className="detail-value">{profileData.personnel.departement || '-'}</span>
                </div>
              </>
            )}

            <button className="btn btn-primary mt-4" onClick={() => setIsEditing(true)}>
              Modifier mon profil
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="profil-form card glass-panel">
            <div className="form-group">
              <label>Nom complet</label>
              <input type="text" name="nom_prenom" value={formData.nom_prenom} onChange={handleInputChange} required />
            </div>
            
            <div className="form-group">
              <label>Email (Non modifiable)</label>
              <input type="email" value={profileData.email} disabled className="disabled-input" />
            </div>

            <div className="form-group">
              <label>Téléphone</label>
              <input type="tel" name="numero_telephone" value={formData.numero_telephone} onChange={handleInputChange} />
            </div>

            {profileData.type_utilisateur === 'etudiant' && (
              <>
                <h3 className="mt-4 mb-2" style={{ color: 'var(--text)' }}>Informations Étudiant</h3>
                <div className="form-group">
                  <label>Numéro Étudiant</label>
                  <input type="text" name="numero_etudiant" value={formData.numero_etudiant} onChange={handleInputChange} />
                </div>
                <div className="form-group">
                  <label>Filière</label>
                  <input type="text" name="filiere" value={formData.filiere} onChange={handleInputChange} />
                </div>
                <div className="form-group">
                  <label>Niveau</label>
                  <input type="text" name="niveau" value={formData.niveau} onChange={handleInputChange} />
                </div>
              </>
            )}

            {profileData.type_utilisateur === 'professeur' && (
              <>
                <h3 className="mt-4 mb-2" style={{ color: 'var(--text)' }}>Informations Professeur</h3>
                <div className="form-group">
                  <label>Spécialité</label>
                  <input type="text" name="specialite" value={formData.specialite} onChange={handleInputChange} />
                </div>
                <div className="form-group">
                  <label>Département</label>
                  <input type="text" name="departement" value={formData.departement} onChange={handleInputChange} />
                </div>
              </>
            )}

            {profileData.type_utilisateur === 'personnel' && (
              <>
                <h3 className="mt-4 mb-2" style={{ color: 'var(--text)' }}>Informations Personnel</h3>
                <div className="form-group">
                  <label>Poste</label>
                  <input type="text" name="poste" value={formData.poste} onChange={handleInputChange} />
                </div>
                <div className="form-group">
                  <label>Département</label>
                  <input type="text" name="departement" value={formData.departement} onChange={handleInputChange} />
                </div>
              </>
            )}

            <div className="form-actions mt-4" style={{ display: 'flex', gap: '1rem' }}>
              <button type="submit" className={`btn btn-primary ${saveLoading ? 'loading' : ''}`} disabled={saveLoading}>
                {saveLoading ? 'Enregistrement...' : 'Enregistrer'}
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => {
                setIsEditing(false);
                setError('');
              }} disabled={saveLoading}>
                Annuler
              </button>
            </div>
          </form>
        )}

        {/* Section Mes Emprunts - Visible uniquement pour Etudiants et Professeurs */}
        {(profileData.type_utilisateur === 'ETUDIANT' || profileData.type_utilisateur === 'PROFESSEUR') && (
          <div className="profil-details card glass-panel mt-4" style={{ marginTop: '2rem' }}>
            <h2>Mes Emprunts</h2>
            <div className="detail-divider"></div>
            {emprunts.length === 0 ? (
              <p style={{ color: 'var(--text-muted)' }}>Vous n'avez aucun emprunt en cours ou passé.</p>
            ) : (
              <div className="emprunts-list" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {emprunts.map(emprunt => {
                  const livre = livres[emprunt.livre_id];
                  const isRetourne = !!emprunt.date_retour_effective;
                  const isRetard = emprunt.en_retard;
                  
                  return (
                    <div key={emprunt.id} style={{ 
                      padding: '1rem', 
                      borderRadius: '8px', 
                      background: 'var(--surface-light)',
                      border: `1px solid ${isRetard ? '#ef4444' : isRetourne ? 'var(--border)' : '#10b981'}`,
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}>
                      <div>
                        <h4 style={{ margin: 0 }}>{livre ? livre.titre : `Livre #${emprunt.livre_id}`}</h4>
                        <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                          Emprunté le {new Date(emprunt.date_emprunt).toLocaleDateString()}
                        </p>
                        <p style={{ margin: 0, fontSize: '0.85rem', color: isRetard ? '#ef4444' : 'var(--text-muted)' }}>
                          Retour prévu le {new Date(emprunt.date_retour_prevue).toLocaleDateString()}
                        </p>
                      </div>
                      <div>
                        {isRetourne ? (
                          <span style={{ padding: '0.25rem 0.75rem', background: '#e5e7eb', borderRadius: '99px', fontSize: '0.8rem', fontWeight: 'bold' }}>
                            Retourné le {new Date(emprunt.date_retour_effective).toLocaleDateString()}
                          </span>
                        ) : (
                          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem' }}>
                            <span className={`badge ${isRetard ? 'badge-danger' : 'badge-warning'}`}>
                              {isRetard ? 'En retard' : 'En cours'}
                            </span>
                            {profileData.type_utilisateur === 'PERSONNEL' && (
                              <button 
                                className="btn btn-outline" 
                                style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}
                                onClick={async () => {
                                  try {
                                    await empruntsService.retournerLivre(emprunt.id);
                                    toast.success("Livre rendu avec succès !");
                                    fetchProfile(user.id_utilisateur);
                                  } catch(e) { toast.error(e.message); }
                                }}
                              >
                                Marquer comme rendu
                              </button>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* ── Section Recommandations Personnalisées ── */}
        {(profileData.type_utilisateur === 'etudiant' || profileData.type_utilisateur === 'professeur') && (
          <div className="profil-details card glass-panel" style={{ marginTop: '2rem' }}>
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              🤖 Livres recommandés pour vous
            </h2>
            <div className="detail-divider"></div>
            {recoLoading ? (
              <p style={{ color: 'var(--text-muted)' }}>Chargement des recommandations…</p>
            ) : recoLivres.length === 0 ? (
              <p style={{ color: 'var(--text-muted)' }}>
                Aucune recommandation disponible pour l'instant — empruntez des livres pour personnaliser vos suggestions !
              </p>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
                {recoLivres.map(livre => (
                  <div
                    key={livre.id}
                    style={{
                      background: 'var(--surface)',
                      borderRadius: '10px',
                      overflow: 'hidden',
                      border: '1px solid var(--border)',
                      transition: 'transform 0.2s',
                      cursor: 'pointer',
                    }}
                    onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-4px)'}
                    onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}
                  >
                    {livre.image_url ? (
                      <img
                        src={livre.image_url}
                        alt={livre.titre}
                        style={{ width: '100%', height: '120px', objectFit: 'cover' }}
                      />
                    ) : (
                      <div style={{
                        height: '120px',
                        background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '2.5rem'
                      }}>📚</div>
                    )}
                    <div style={{ padding: '0.75rem' }}>
                      <p style={{ margin: 0, fontWeight: '600', fontSize: '0.85rem', color: 'var(--text)', lineHeight: '1.3' }}>
                        {livre.titre}
                      </p>
                      <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {livre.auteur}
                      </p>
                      <span style={{
                        display: 'inline-block',
                        marginTop: '0.5rem',
                        padding: '0.15rem 0.5rem',
                        background: 'rgba(var(--primary-rgb, 99,102,241), 0.15)',
                        color: 'var(--primary)',
                        borderRadius: '99px',
                        fontSize: '0.7rem',
                        fontWeight: '600'
                      }}>
                        {livre.categorie}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
            <div style={{ marginTop: '1rem', textAlign: 'right' }}>
              <Link to="/catalogue" className="btn btn-outline" style={{ fontSize: '0.85rem', padding: '0.4rem 1rem' }}>
                Voir tout le catalogue →
              </Link>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default Profil;
