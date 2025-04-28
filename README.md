# YouTube Downloader

Une application de bureau pour télécharger des vidéos YouTube en différents formats.

## Prérequis

- Python 3.8 ou supérieur
- MongoDB installé et en cours d'exécution
- pip (gestionnaire de paquets Python)

## Installation

1. Clonez ce dépôt :
```bash
git clone [URL_DU_REPO]
cd projet
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Assurez-vous que MongoDB est en cours d'exécution sur votre machine.

4. Configurez les variables d'environnement dans le fichier `.env` si nécessaire.

## Utilisation

1. Démarrez le serveur backend :
```bash
python app.py
```

2. Dans un autre terminal, lancez l'interface utilisateur :
```bash
python ui.py
```

3. L'application s'ouvrira avec une interface graphique où vous pourrez :
   - Entrer l'URL de la vidéo YouTube
   - Choisir le format de téléchargement (MP4, MP3)
   - Sélectionner la qualité
   - Télécharger la vidéo
   - Consulter l'historique des téléchargements

## Fonctionnalités

- Téléchargement de vidéos YouTube en MP4 et MP3
- Choix de la qualité (meilleure qualité, 720p, 1080p)
- Historique des téléchargements
- Interface utilisateur intuitive
- Barre de progression
- Gestion des erreurs

## Structure du Projet

```
projet/
├── app.py           # API FastAPI
├── ui.py            # Interface utilisateur Tkinter
├── requirements.txt # Dépendances Python
├── .env            # Variables d'environnement
└── README.md       # Documentation
```

## Notes

- Les vidéos téléchargées sont stockées dans le dossier `downloads/`
- L'historique des téléchargements est stocké dans MongoDB
- Assurez-vous d'avoir suffisamment d'espace disque pour les téléchargements 