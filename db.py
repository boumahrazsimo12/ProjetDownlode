from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Chargement des variables d'environnement
load_dotenv()

# Connexion à MongoDB
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGODB_URI)
db = client["youtube_downloader"]

# Collections
users = db["users"]
downloads = db["downloads"]
profiles = db["profiles"]

# Création des index
users.create_index("username", unique=True)
users.create_index("email", unique=True)
downloads.create_index([("user_id", 1), ("download_date", -1)])
