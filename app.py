from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import yt_dlp
import os

from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter
import json
import subprocess

# Chargement des variables d'environnement
load_dotenv()

# Configuration FastAPI
app = FastAPI(title="YouTube Downloader API")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connexion à MongoDB
client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))
db = client.youtube_downloader
downloads = db.downloads
users_collection = db["users"]

class DownloadRequest(BaseModel):
    url: str
    format: str = "mp4"
    quality: Optional[str] = "best"

# Fonction pour gérer les placeholders
def on_enter(e, widget, default_text):
    if widget.get() == default_text:
        widget.delete(0, 'end')
        widget.config(fg='black')

def on_leave(e, widget, default_text):
    if widget.get() == '':
        widget.insert(0, default_text)
        widget.config(fg='gray')

def signin():
    username = user.get()
    password = code.get()

    user_data = users_collection.find_one({"username": username})

    if user_data and user_data["password"] == password:
        # Stocker l'utilisateur connecté dans session.json
        with open("session.json", "w") as f:
            json.dump({
                "username": username,
                "user_id": str(user_data["_id"]),
                "logged_in": True
            }, f)

        root.destroy()  # Fermer la fenêtre de connexion
        subprocess.run(["python", "ui.py"])  # Ouvrir l'interface principale
    else:
        messagebox.showerror('Invalid', 'User not found or incorrect password')

def signup_window():
    root.withdraw()  # Cacher la fenêtre principale (Login)
    window = tk.Toplevel(root)
    window.title('Sign Up')
    window.geometry('925x500+300+200')
    window.configure(bg="#fff")
    window.resizable(False, False)

    def register():
        username = user_entry.get()
        password = code_entry.get()
        confirm_password = confirm_code_entry.get()

        if password == confirm_password:
            existing_user = users_collection.find_one({"username": username})
            if existing_user:
                messagebox.showerror('Error', 'Username already exists')
            else:
                # Add email field as None initially
                users_collection.insert_one({
                    "username": username,
                    "password": password,
                    "email": None  # Initialize email as None
                })
                messagebox.showinfo('Signup', 'Successfully signed up')
                window.destroy()
                root.deiconify()
        else:
            messagebox.showerror('Invalid', 'Both passwords should match')

    frame = tk.Frame(window, width=350, height=390, bg='white')
    frame.place(x=480, y=50)

    heading = tk.Label(frame, text='Sign up', fg='#57a1f8', bg='white', 
                      font=('Microsoft YaHei UI Light', 23, 'bold'))
    heading.place(x=100, y=5)

    # Username field
    user_entry = tk.Entry(frame, width=25, fg='gray', border=0, bg='white', 
                         font=('Microsoft YaHei UI Light', 11))
    user_entry.place(x=30, y=80)
    user_entry.insert(0, 'Username')
    user_entry.bind("<FocusIn>", lambda e: on_enter(e, user_entry, 'Username'))
    user_entry.bind("<FocusOut>", lambda e: on_leave(e, user_entry, 'Username'))
    tk.Frame(frame, width=295, height=2, bg='black').place(x=25, y=107)

    # Password field
    code_entry = tk.Entry(frame, width=25, fg='gray', border=0, bg='white', 
                         font=('Microsoft YaHei UI Light', 11))
    code_entry.place(x=30, y=150)
    code_entry.insert(0, 'Password')
    code_entry.bind("<FocusIn>", lambda e: on_enter(e, code_entry, 'Password'))
    code_entry.bind("<FocusOut>", lambda e: on_leave(e, code_entry, 'Password'))
    tk.Frame(frame, width=295, height=2, bg='black').place(x=25, y=177)

    # Confirm Password field
    confirm_code_entry = tk.Entry(frame, width=25, fg='gray', border=0, bg='white', 
                                font=('Microsoft YaHei UI Light', 11))
    confirm_code_entry.place(x=30, y=220)
    confirm_code_entry.insert(0, 'Confirm Password')
    confirm_code_entry.bind("<FocusIn>", lambda e: on_enter(e, confirm_code_entry, 'Confirm Password'))
    confirm_code_entry.bind("<FocusOut>", lambda e: on_leave(e, confirm_code_entry, 'Confirm Password'))
    tk.Frame(frame, width=295, height=2, bg='black').place(x=25, y=247)

    # Register button
    tk.Button(frame, width=39, pady=7, text='Sign up', bg='#57a1f8', fg='white', 
              border=0, command=register).place(x=35, y=280)

    window.protocol("WM_DELETE_WINDOW", lambda: (window.destroy(), root.deiconify()))

# Routes FastAPI
@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API YouTube Downloader"}

@app.post("/download")
async def download_video(request: DownloadRequest):
    try:
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }

        if request.format == "mp3":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        elif request.format == "mp4":
            if request.quality == "1080p":
                ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
            elif request.quality == "720p":
                ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
            else:
                ydl_opts['format'] = 'bestvideo+bestaudio/best'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=True)
            
            download_record = {
                "title": info.get("title"),
                "url": request.url,
                "format": request.format,
                "quality": request.quality,
                "download_date": datetime.now(),
                "file_path": f"downloads/{info.get('title')}.{request.format}"
            }
            downloads.insert_one(download_record)

            return {
                "message": "Téléchargement réussi",
                "title": info.get("title"),
                "format": request.format
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_history():
    try:
        history = list(downloads.find({}, {"_id": 0}))
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Création de la fenêtre principale de login
    root = tk.Tk()
    root.title('Login')
    root.geometry('925x500+300+200')
    root.configure(bg='#fff')
    root.resizable(False, False)

    # Interface de connexion
    frame = tk.Frame(root, width=350, height=350, bg='white')
    frame.place(x=480, y=70)

    heading = tk.Label(frame, text='Sign in', fg='#57a1f8', bg='white', 
                      font=('Microsoft YaHei UI Light', 23, 'bold'))
    heading.place(x=100, y=5)

    # Username field
    user = tk.Entry(frame, width=25, fg='gray', border=0, bg='white', 
                   font=('Microsoft YaHei UI Light', 11))
    user.place(x=30, y=80)
    user.insert(0, 'Username')
    user.bind('<FocusIn>', lambda e: on_enter(e, user, 'Username'))
    user.bind('<FocusOut>', lambda e: on_leave(e, user, 'Username'))
    tk.Frame(frame, width=295, height=2, bg='black').place(x=25, y=107)

    # Password field
    code = tk.Entry(frame, width=25, fg='gray', border=0, bg='white', 
                   font=('Microsoft YaHei UI Light', 11))
    code.place(x=30, y=150)
    code.insert(0, 'Password')
    code.bind('<FocusIn>', lambda e: on_enter(e, code, 'Password'))
    code.bind('<FocusOut>', lambda e: on_leave(e, code, 'Password'))
    tk.Frame(frame, width=295, height=2, bg='black').place(x=25, y=177)

    # Login button
    tk.Button(frame, width=39, pady=7, text='Sign in', bg='#57a1f8', fg='white', 
              border=0, command=signin).place(x=35, y=204)

    # Sign up link
    tk.Label(frame, text="Don't have an account?", fg='black', bg='white', 
             font=('Microsoft YaHei UI Light', 9)).place(x=75, y=270)

    tk.Button(frame, width=6, text='Sign up', border=0, bg='white', cursor='hand2', 
              fg='#57a1f8', command=signup_window).place(x=215, y=270)

    # Démarrer le serveur FastAPI dans un thread séparé
    import threading
    import uvicorn

    def run_server():
        uvicorn.run(app, host="0.0.0.0", port=8000)

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Démarrer l'interface graphique
    root.mainloop()