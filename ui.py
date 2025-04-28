import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import requests
import json
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import os
from db import users, profiles, downloads
import threading
import base64
from io import BytesIO
import subprocess

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Vérifier la session
        try:
            with open("session.json", "r") as f:
                self.session = json.load(f)
                self.current_user = users.find_one({"username": self.session["username"]})
                if not self.current_user:
                    raise Exception("Utilisateur non trouvé")
        except Exception as e:
            messagebox.showerror("Erreur", "Session invalide. Veuillez vous reconnecter.")
            self.destroy()
            return
        
        # Configuration de base
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.title(f"YouTube Downloader - {self.session['username']}")
        self.geometry("1100x700")
        
        # Création de l'interface principale
        self.main_frame = MainFrame(self)
        self.main_frame.pack(fill="both", expand=True)

    def show_profile(self):
        profile_window = ProfileWindow(self)
        profile_window.grab_set()

    def logout(self):
        try:
            os.remove("session.json")
        except:
            pass
        self.destroy()
        # Lancer l'application de login
        subprocess.Popen(["python", "app.py"])

class ProfileWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        
        self.title("Profil Utilisateur")
        self.geometry("400x600")
        
        # Container principal
        container = ctk.CTkFrame(self, corner_radius=20, fg_color="#ffffff")
        container.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Titre
        ctk.CTkLabel(container,
                    text="Profil Utilisateur",
                    font=("Arial", 28, "bold"),
                    text_color="#222831").pack(pady=20)
        
        # Frame Avatar
        avatar_frame = ctk.CTkFrame(container, fg_color="transparent")
        avatar_frame.pack(pady=20)
        
        self.avatar_label = ctk.CTkLabel(avatar_frame, text="", width=150, height=150)
        self.avatar_label.pack()
        
        change_avatar_btn = ctk.CTkButton(
            avatar_frame,
            text="Changer l'avatar",
            command=self.change_avatar,
            fg_color="#393E46",
            hover_color="#222831",
            width=200,
            corner_radius=15
        )
        change_avatar_btn.pack(pady=10)
        
        # Informations utilisateur
        user_frame = ctk.CTkFrame(container, fg_color="transparent")
        user_frame.pack(pady=20, padx=20, fill="x")
        
        # Nom d'utilisateur
        username_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
        username_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(username_frame,
                    text="Nom d'utilisateur:",
                    font=("Arial", 12),
                    text_color="#222831").pack(side="left")
        
        self.username_entry = ctk.CTkEntry(
            username_frame,
            width=200,
            height=30,
            corner_radius=10,
            fg_color="#EAEAEA",
            border_color="#CCCCCC",
            text_color="#222831"
        )
        self.username_entry.pack(side="right", padx=5)
        self.username_entry.insert(0, self.master.session["username"])
        
        # Mot de passe
        password_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
        password_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(password_frame,
                    text="Nouveau mot de passe:",
                    font=("Arial", 12),
                    text_color="#222831").pack(side="left")
        
        self.password_entry = ctk.CTkEntry(
            password_frame,
            width=200,
            height=30,
            corner_radius=10,
            fg_color="#EAEAEA",
            border_color="#CCCCCC",
            text_color="#222831",
            show="*"
        )
        self.password_entry.pack(side="right", padx=5)
        
        # Confirmation mot de passe
        confirm_password_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
        confirm_password_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(confirm_password_frame,
                    text="Confirmer le mot de passe:",
                    font=("Arial", 12),
                    text_color="#222831").pack(side="left")
        
        self.confirm_password_entry = ctk.CTkEntry(
            confirm_password_frame,
            width=200,
            height=30,
            corner_radius=10,
            fg_color="#EAEAEA",
            border_color="#CCCCCC",
            text_color="#222831",
            show="*"
        )
        self.confirm_password_entry.pack(side="right", padx=5)
        
        # Bio
        bio_frame = ctk.CTkFrame(container, fg_color="transparent")
        bio_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(bio_frame,
                    text="Biographie:",
                    font=("Arial", 16),
                    text_color="#222831").pack(anchor="w")
        
        self.bio_text = ctk.CTkTextbox(
            bio_frame,
            height=100,
            width=400,
            corner_radius=15,
            fg_color="#EAEAEA",
            border_color="#CCCCCC",
            text_color="#222831"
        )
        self.bio_text.pack(pady=10, fill="x")
        
        # Boutons
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(pady=20)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Sauvegarder",
            command=self.save_profile,
            fg_color="#393E46",
            hover_color="#222831",
            width=140,
            corner_radius=15
        )
        save_btn.pack(side="left", padx=5)
        
        self.load_profile()

    def load_profile(self):
        try:
            profile = profiles.find_one({"user_id": self.master.current_user["_id"]})
            if profile:
                self.bio_text.delete("1.0", tk.END)
                self.bio_text.insert("1.0", profile.get("bio", ""))
                
                if profile.get("avatar"):
                    try:
                        # Si l'avatar est stocké en base64
                        if isinstance(profile["avatar"], str) and profile["avatar"].startswith("data:image"):
                            # Extraire la partie base64 de l'image
                            img_data = profile["avatar"].split(",")[1]
                            img_bytes = base64.b64decode(img_data)
                            img = Image.open(BytesIO(img_bytes))
                        else:
                            # Si c'est un chemin de fichier
                            img = Image.open(profile["avatar"])
                        
                        img = img.resize((150, 150))
                        mask = Image.new("L", (150, 150), 0)
                        draw = ImageDraw.Draw(mask)
                        draw.ellipse((0, 0, 150, 150), fill=255)
                        output = Image.new("RGBA", (150, 150), (0, 0, 0, 0))
                        output.paste(img, (0, 0))
                        output.putalpha(mask)
                        
                        photo = ImageTk.PhotoImage(output)
                        self.avatar_label.configure(image=photo)
                        self.avatar_label.image = photo
                    except Exception as e:
                        print(f"Erreur lors du chargement de l'avatar: {str(e)}")
                        self.avatar_label.configure(text="Avatar non disponible")
                else:
                    self.avatar_label.configure(text="Aucun avatar")
        except Exception as e:
            print(f"Erreur lors du chargement du profil: {str(e)}")
            messagebox.showerror("Erreur", f"Erreur lors du chargement du profil: {str(e)}")

    def change_avatar(self):
        filename = filedialog.askopenfilename(
            title="Choisir un avatar",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if filename:
            try:
                # Convertir l'image en base64
                with open(filename, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()
                
                # Stocker l'image en base64 dans MongoDB
                profiles.update_one(
                    {"user_id": self.master.current_user["_id"]},
                    {"$set": {"avatar": f"data:image/jpeg;base64,{encoded_string}"}},
                    upsert=True
                )
                self.load_profile()
                messagebox.showinfo("Succès", "Avatar mis à jour!")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la mise à jour de l'avatar: {str(e)}")

    def save_profile(self):
        try:
            # Vérifier le mot de passe
            new_password = self.password_entry.get()
            confirm_password = self.confirm_password_entry.get()
            
            if new_password and new_password != confirm_password:
                messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas")
                return
            
            # Mettre à jour le profil
            profile_data = {
                "bio": self.bio_text.get("1.0", tk.END).strip()
            }
            
            # Mettre à jour le nom d'utilisateur si changé
            new_username = self.username_entry.get()
            if new_username != self.master.session["username"]:
                # Vérifier si le nom d'utilisateur existe déjà
                if users.find_one({"username": new_username}):
                    messagebox.showerror("Erreur", "Ce nom d'utilisateur est déjà utilisé")
                    return
                
                # Mettre à jour le nom d'utilisateur
                users.update_one(
                    {"_id": self.master.current_user["_id"]},
                    {"$set": {"username": new_username}}
                )
                self.master.session["username"] = new_username
                self.master.title(f"YouTube Downloader - {new_username}")
            
            # Mettre à jour le mot de passe si changé
            if new_password:
                users.update_one(
                    {"_id": self.master.current_user["_id"]},
                    {"$set": {"password": new_password}}
                )
            
            # Mettre à jour le profil
            profiles.update_one(
                {"user_id": self.master.current_user["_id"]},
                {"$set": profile_data},
                upsert=True
            )
            
            messagebox.showinfo("Succès", "Profil mis à jour!")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la mise à jour du profil: {str(e)}")

class MainFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # Container principal
        container = ctk.CTkFrame(self, corner_radius=20, fg_color="#ffffff")
        container.pack(padx=20, pady=20, fill="both", expand=True)
        
        # En-tête
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(header_frame,
                    text="YouTube Downloader",
                    font=("Arial", 24, "bold"),
                    text_color="#222831").pack(side="left")
        
        # Boutons de droite
        buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        buttons_frame.pack(side="right")
        
        # Avatar et nom d'utilisateur
        user_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        user_frame.pack(side="left", padx=10)
        
        # Charger l'avatar de l'utilisateur
        self.load_user_avatar(user_frame)
        
        # Nom d'utilisateur
        ctk.CTkLabel(
            user_frame,
            text=master.session["username"],
            font=("Arial", 12),
            text_color="#222831"
        ).pack(side="left", padx=5)
        
        profile_btn = ctk.CTkButton(
            buttons_frame,
            text="Profil",
            command=lambda: master.show_profile(),
            fg_color="#393E46",
            hover_color="#222831",
            width=100,
            corner_radius=15
        )
        profile_btn.pack(side="left", padx=5)
        
        logout_btn = ctk.CTkButton(
            buttons_frame,
            text="Déconnexion",
            command=lambda: master.logout(),
            fg_color="#dc3545",
            hover_color="#c82333",
            width=100,
            corner_radius=15
        )
        logout_btn.pack(side="left", padx=5)
        
        # URL Entry
        url_frame = ctk.CTkFrame(container, fg_color="transparent")
        url_frame.pack(fill="x", padx=20, pady=10)
        
        self.url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="URL YouTube",
            width=400,
            height=40,
            corner_radius=15,
            fg_color="#EAEAEA",
            border_color="#CCCCCC",
            text_color="#222831"
        )
        self.url_entry.pack(fill="x", pady=10)
        
        # Options
        options_frame = ctk.CTkFrame(container, fg_color="transparent")
        options_frame.pack(fill="x", padx=20, pady=10)
        
        # Format
        format_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        format_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(format_frame, text="Format:").pack(side="left")
        self.format_var = tk.StringVar(value="mp4")
        format_combo = ctk.CTkOptionMenu(
            format_frame,
            values=["mp4", "mp3"],
            variable=self.format_var,
            fg_color="#393E46",
            button_color="#222831",
            button_hover_color="#000000"
        )
        format_combo.pack(side="left", padx=5)
        
        # Qualité
        quality_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        quality_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(quality_frame, text="Qualité:").pack(side="left")
        self.quality_var = tk.StringVar(value="best")
        quality_combo = ctk.CTkOptionMenu(
            quality_frame,
            values=["best", "720p", "1080p"],
            variable=self.quality_var,
            fg_color="#393E46",
            button_color="#222831",
            button_hover_color="#000000"
        )
        quality_combo.pack(side="left", padx=5)
        
        # Download Button
        self.download_btn = ctk.CTkButton(
            container,
            text="Télécharger",
            command=self.start_download,
            fg_color="#393E46",
            hover_color="#222831",
            width=200,
            height=40,
            corner_radius=15,
            font=("Arial", 14, "bold")
        )
        self.download_btn.pack(pady=20)
        
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(container, width=400)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)
        
        # Status Label
        self.status_label = ctk.CTkLabel(
            container,
            text="",
            font=("Arial", 12),
            text_color="#222831"
        )
        self.status_label.pack(pady=5)
        
        # History
        history_frame = ctk.CTkFrame(container, fg_color="transparent")
        history_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(history_frame,
                    text="Historique des téléchargements",
                    font=("Arial", 16, "bold"),
                    text_color="#222831").pack(pady=10)
        
        # Tableau d'historique
        self.history_tree = ttk.Treeview(
            history_frame,
            columns=("Date", "Titre", "Format"),
            show="headings"
        )
        
        self.history_tree.heading("Date", text="Date")
        self.history_tree.heading("Titre", text="Titre")
        self.history_tree.heading("Format", text="Format")
        
        self.history_tree.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.load_history()

    def load_user_avatar(self, parent):
        try:
            profile = profiles.find_one({"user_id": self.master.current_user["_id"]})
            if profile and profile.get("avatar"):
                # Si l'avatar est stocké en base64
                if isinstance(profile["avatar"], str) and profile["avatar"].startswith("data:image"):
                    img_data = profile["avatar"].split(",")[1]
                    img_bytes = base64.b64decode(img_data)
                    img = Image.open(BytesIO(img_bytes))
                else:
                    img = Image.open(profile["avatar"])
                
                # Redimensionner l'avatar
                img = img.resize((30, 30))
                
                # Créer un masque circulaire
                mask = Image.new("L", (30, 30), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, 30, 30), fill=255)
                
                # Appliquer le masque
                output = Image.new("RGBA", (30, 30), (0, 0, 0, 0))
                output.paste(img, (0, 0))
                output.putalpha(mask)
                
                # Créer le widget pour l'avatar
                photo = ImageTk.PhotoImage(output)
                avatar_label = ctk.CTkLabel(
                    parent,
                    text="",
                    width=30,
                    height=30
                )
                avatar_label.configure(image=photo)
                avatar_label.image = photo
                avatar_label.pack(side="left", padx=5)
        except Exception as e:
            print(f"Erreur lors du chargement de l'avatar: {str(e)}")
            # Afficher un avatar par défaut ou une icône
            avatar_label = ctk.CTkLabel(
                parent,
                text="👤",
                width=30,
                height=30
            )
            avatar_label.pack(side="left", padx=5)

    def start_download(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Erreur", "Veuillez entrer une URL YouTube")
            return
            
        self.download_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="Préparation du téléchargement...")
        
        # Démarrer le téléchargement dans un thread séparé
        thread = threading.Thread(target=self.download_video, args=(url,))
        thread.daemon = True
        thread.start()

    def download_video(self, url):
        try:
            # Démarrer le téléchargement
            response = requests.post(
                "http://localhost:8000/download",
                json={
                    "url": url,
                    "format": self.format_var.get(),
                    "quality": self.quality_var.get(),
                    "user_id": str(self.master.current_user["_id"])
                }
            )
            
            if response.status_code == 200:
                # Mettre à jour la progression
                self.progress_bar.set(1)
                self.status_label.configure(text="Téléchargement terminé!")
                
                # Récupérer les informations du téléchargement
                download_info = response.json()
                
                # Sauvegarder dans la base de données
                try:
                    downloads.insert_one({
                        "user_id": str(self.master.current_user["_id"]),
                        "title": download_info.get("title", "Titre inconnu"),
                        "format": self.format_var.get(),
                        "download_date": datetime.now(),
                        "url": url
                    })
                    print("Téléchargement enregistré dans la base de données")  # Debug
                except Exception as e:
                    print(f"Erreur lors de l'enregistrement du téléchargement: {str(e)}")
                
                messagebox.showinfo("Succès", "Téléchargement réussi!")
                self.load_history()  # Recharger l'historique
            else:
                self.status_label.configure(text="Erreur lors du téléchargement")
                messagebox.showerror("Erreur", f"Erreur lors du téléchargement: {response.text}")
                
        except Exception as e:
            self.status_label.configure(text="Erreur de connexion")
            messagebox.showerror("Erreur", f"Erreur de connexion: {str(e)}")
        finally:
            self.download_btn.configure(state="normal")

    def load_history(self):
        try:
            # Récupérer l'historique des téléchargements
            user_downloads = list(downloads.find(
                {"user_id": str(self.master.current_user["_id"])}  # Convertir l'ID en string
            ).sort("download_date", -1))
            
            print(f"Téléchargements trouvés : {len(user_downloads)}")  # Debug
            
            # Vider le tableau
            self.history_tree.delete(*self.history_tree.get_children())
            
            # Ajouter chaque téléchargement
            for item in user_downloads:
                try:
                    # Convertir la date en format lisible
                    if "download_date" in item:
                        date = datetime.fromisoformat(str(item["download_date"])).strftime("%Y-%m-%d %H:%M")
                    else:
                        date = "Date inconnue"
                    
                    # Récupérer le titre et le format
                    title = item.get("title", "Titre inconnu")
                    format_type = item.get("format", "Format inconnu")
                    
                    print(f"Ajout d'un élément : {date} - {title} - {format_type}")  # Debug
                    
                    # Insérer dans le tableau
                    self.history_tree.insert("", "end", values=(date, title, format_type))
                except Exception as e:
                    print(f"Erreur lors de l'ajout d'un élément à l'historique: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Erreur lors du chargement de l'historique: {str(e)}")
            messagebox.showerror("Erreur", f"Erreur lors du chargement de l'historique: {str(e)}")

if __name__ == "__main__":
    app = App()
    app.mainloop() 