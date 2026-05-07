import requests
import time

LIVRES_API_URL = "http://localhost:8001/livres/"

livres = [
    {
        "titre": "L'Étranger",
        "auteur": "Albert Camus",
        "isbn": "9782070360024",
        "annee_publication": 1942,
        "categorie": "Roman",
        "description": "Un chef-d'œuvre de l'absurde racontant l'histoire de Meursault.",
        "quantite_totale": 5,
        "quantite_disponible": 5,
        "image_url": "https://m.media-amazon.com/images/I/41-1vW5D3cL._SY445_SX342_.jpg"
    },
    {
        "titre": "1984",
        "auteur": "George Orwell",
        "isbn": "9782070368228",
        "annee_publication": 1949,
        "categorie": "Science-Fiction",
        "description": "Une dystopie terrifiante sur un monde surveillé par Big Brother.",
        "quantite_totale": 3,
        "quantite_disponible": 3,
        "image_url": "https://m.media-amazon.com/images/I/51wXpMvWpSL._SY445_SX342_.jpg"
    },
    {
        "titre": "Le Petit Prince",
        "auteur": "Antoine de Saint-Exupéry",
        "isbn": "9782070612758",
        "annee_publication": 1943,
        "categorie": "Conte",
        "description": "Un conte poétique et philosophique pour petits et grands.",
        "quantite_totale": 10,
        "quantite_disponible": 10,
        "image_url": "https://m.media-amazon.com/images/I/51n5X2668KL._SY445_SX342_.jpg"
    },
    {
        "titre": "Les Misérables",
        "auteur": "Victor Hugo",
        "isbn": "9782253096337",
        "annee_publication": 1862,
        "categorie": "Classique",
        "description": "L'épopée de Jean Valjean dans la France du XIXe siècle.",
        "quantite_totale": 2,
        "quantite_disponible": 2,
        "image_url": "https://m.media-amazon.com/images/I/41t7+uXlq-L._SY445_SX342_.jpg"
    },
    {
        "titre": "Dune",
        "auteur": "Frank Herbert",
        "isbn": "9782266320481",
        "annee_publication": 1965,
        "categorie": "Science-Fiction",
        "description": "L'histoire de Paul Atréides sur la planète désertique d'Arrakis.",
        "quantite_totale": 4,
        "quantite_disponible": 4,
        "image_url": "https://m.media-amazon.com/images/I/41zYdE+pM9L._SY445_SX342_.jpg"
    },
    {
        "titre": "Clean Code",
        "auteur": "Robert C. Martin",
        "isbn": "9780132350884",
        "annee_publication": 2008,
        "categorie": "Informatique",
        "description": "Les bonnes pratiques pour écrire du code propre et maintenable.",
        "quantite_totale": 6,
        "quantite_disponible": 6,
        "image_url": "https://m.media-amazon.com/images/I/41xShlnTZTL._SY445_SX342_.jpg"
    },
    {
        "titre": "Design Patterns",
        "auteur": "Gang of Four",
        "isbn": "9780201633610",
        "annee_publication": 1994,
        "categorie": "Informatique",
        "description": "Les bases de la conception orientée objet.",
        "quantite_totale": 2,
        "quantite_disponible": 2,
        "image_url": "https://m.media-amazon.com/images/I/51szD9HC9pL._SY445_SX342_.jpg"
    },
    {
        "titre": "Fondation",
        "auteur": "Isaac Asimov",
        "isbn": "9782070360536",
        "annee_publication": 1951,
        "categorie": "Science-Fiction",
        "description": "Hari Seldon prévoit la chute de l'Empire Galactique.",
        "quantite_totale": 3,
        "quantite_disponible": 3,
        "image_url": "https://m.media-amazon.com/images/I/51bA9k49hLL._SY445_SX342_.jpg"
    }
]

def seed_db():
    print("Peuplement de la base de donnees des livres en cours...")
    success = 0
    for livre in livres:
        # Adaptation aux nouveaux noms de champs du backend
        payload = livre.copy()
        payload["exemplaires_totaux"] = payload.pop("quantite_totale", 1)
        # On ignore quantite_disponible car on utilise uniquement exemplaires_totaux
        payload.pop("quantite_disponible", None)
        
        try:
            response = requests.post(LIVRES_API_URL, json=payload)
            if response.status_code == 201 or response.status_code == 200:
                print(f"[OK] Ajoute : {livre['titre']}")
                success += 1
            else:
                print(f"[ERREUR] Pour {livre['titre']}: {response.text}")
        except requests.exceptions.ConnectionError:
            print("[ERREUR] Connexion impossible: Le service livres n'est pas en cours d'execution sur le port 8001.")
            break
    print(f"\nTermine ! {success}/{len(livres)} livres ajoutes.")

if __name__ == "__main__":
    seed_db()
