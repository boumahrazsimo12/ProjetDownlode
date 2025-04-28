import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading
import yt_dlp
from PIL import Image, ImageTk
import os
import json
import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["test"]
users_collection = db["users"]

root = tk.Tk()
root.geometry('700x600')
root.title('Tkinter Ultimate')

menu_bar_colour = '#383838'

# Charger la session de l'utilisateur
with open("session.json", "r") as file:
    session = json.load(file)
current_username = session.get("username", "")

# Récupérer les données de l'utilisateur depuis MongoDB
user_data = users_collection.find_one({"username": current_username}) or {}

def get_profile_image():
    """ Charge l'image de profil de l'utilisateur ou une image par défaut """
    img_path = user_data.get("profile_image", "default.jpg")
    if not os.path.exists(img_path):
        img = Image.new("RGB", (100, 100), "gray")  # Image grise par défaut
    else:
        img = Image.open(img_path).resize((100, 100))

    return ImageTk.PhotoImage(img)

def update_profile_icon():
    """ Met à jour l'icône de profil après modification """
    new_profile_img = get_profile_image()
    update_btn.configure(image=new_profile_img)
    update_btn.image = new_profile_img  # Garde une référence pour éviter la suppression par le GC

def switch_indication(indicator_lb, page):
    home_btn_indicator.config(bg=menu_bar_colour)
    service_btn_indicator.config(bg=menu_bar_colour)
    update_btn_indicator.config(bg=menu_bar_colour)
    indicator_lb.config(bg='white')

    for frame in page_frame.winfo_children():
        frame.destroy()
    page()

def service_page():
    spacer = tk.Frame(page_frame, height=80)
    spacer.pack(fill='x', side='top')
    home_page_fm = tk.Frame(page_frame)

    status = tk.Label(home_page_fm, text="Status: Ready", font="Calibre 10 italic", fg="grey", bg="white", anchor="w")
    status.place(rely=1, anchor="sw", relwidth=1)

    def Browse():
        directory = filedialog.askdirectory(title="Save Directory")
        folderLink.delete(0, "end")
        folderLink.insert(0, directory)

    def down_yt():
        status.config(text="Status: Downloading...")
        link = ytLink.get()
        folder = folderLink.get()


        def hook(d):
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', '0.0%').replace('%', '').strip()
                progress['value'] = float(percent)
                status.config(text=f"Status: Downloading... {percent}%")
                home_page_fm.update_idletasks()
            elif d['status'] == 'finished':
                progress['value'] = 100
                status.config(text="Status: Download Complete")

        ydl_opts = {
            'outtmpl': f'{folder}/%(title)s.%(ext)s',
            'progress_hooks': [hook]
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
        except Exception as e:
            status.config(text=f"Error: {str(e)}")

    ytLabel = tk.Label(home_page_fm, text="YouTube Link")
    ytLabel.place(x=25, y=150)

    ytLink = tk.Entry(home_page_fm, width=50)
    ytLink.place(x=140, y=150)

    folderLabel = tk.Label(home_page_fm, text="Download Folder")
    folderLabel.place(x=25, y=183)

    folderLink = tk.Entry(home_page_fm, width=50)
    folderLink.place(x=140, y=183)

    browse = tk.Button(home_page_fm, text="Browse", bg="Yellow", command=Browse)
    browse.place(x=455, y=180)

    thread_btn = lambda: threading.Thread(target=down_yt).start()
    download = tk.Button(home_page_fm, text="Download", bg="red", fg="white", command=thread_btn)
    download.place(x=280, y=220)

    progress = ttk.Progressbar(home_page_fm, orient="horizontal", length=400, mode="determinate")
    progress.place(x=100, y=270)

    home_page_fm.pack(fill=tk.BOTH, expand=True)
def home_page():
    home_frame = tk.Frame(page_frame)
    lb = tk.Label(home_frame, text='Home Page', font=('bold', 20))
    lb.place(x=100, y=200)
    home_frame.pack(fill=tk.BOTH, expand=True)

def update_page():
    """ Page de mise à jour du profil """
    update_page_fm = tk.Frame(page_frame)

    profile_img = get_profile_image()
    profile_label = tk.Label(update_page_fm, image=profile_img)
    profile_label.image = profile_img
    profile_label.pack(pady=10)

    def select_image():
        """ Sélectionne une image et l'affiche """
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if file_path:
            user_data["profile_image"] = file_path
            img = Image.open(file_path).resize((100, 100))
            img = ImageTk.PhotoImage(img)
            profile_label.configure(image=img)
            profile_label.image = img  

    change_img_btn = tk.Button(update_page_fm, text="Change Image", command=select_image, bg="#00ADB5", fg="white")
    change_img_btn.pack(pady=5)

    tk.Label(update_page_fm, text="Username:", font=("Arial", 14)).pack()
    username_entry = tk.Entry(update_page_fm, width=30)
    username_entry.insert(0, user_data.get("username", ""))
    username_entry.pack(pady=5)

    tk.Label(update_page_fm, text="Password:", font=("Arial", 14)).pack()
    password_entry = tk.Entry(update_page_fm, width=30, show="*")
    password_entry.pack(pady=5)

    def save_changes():
        """ Enregistre les modifications dans la base de données """
        global current_username
        new_username = username_entry.get()
        new_password = password_entry.get()
        new_profile_image = user_data.get("profile_image", "default.jpg")

        if not new_username or not new_password:
            messagebox.showerror("Error", "Both fields are required!")
            return

        users_collection.update_one(
            {"username": current_username},
            {"$set": {"username": new_username, "password": new_password, "profile_image": new_profile_image}}
        )

        current_username = new_username
        session["username"] = new_username
        with open("session.json", "w") as file:
            json.dump(session, file)

        update_profile_icon()
        messagebox.showinfo("Success", "Profile updated successfully!")
        switch_indication(indicator_lb=home_btn_indicator, page=home_page)

    save_button = tk.Button(update_page_fm, text="Save Changes", command=save_changes, bg="#00ADB5", fg="white")
    save_button.pack(pady=10)

    update_page_fm.pack(fill=tk.BOTH, expand=True)

# Création du cadre principal
page_frame = tk.Frame(root)
page_frame.place(relwidth=1.0, relheight=1.0, x=50)
home_page()

# Création de la barre de menu
menu_bar_frame = tk.Frame(root, bg=menu_bar_colour)

home_btn = tk.Button(menu_bar_frame, text="🏠", font=("Arial", 14), bg=menu_bar_colour, bd=0, activebackground=menu_bar_colour, 
                     command=lambda: switch_indication(indicator_lb=home_btn_indicator, page=home_page))
home_btn.place(x=9, y=130, width=30, height=40)
home_btn_indicator = tk.Label(menu_bar_frame, bg='white')
home_btn_indicator.place(x=3, y=130, width=3, height=40)

service_btn = tk.Button(menu_bar_frame, text="📺", font=("Arial", 14), bg=menu_bar_colour, bd=0, activebackground=menu_bar_colour, command=lambda: switch_indication(indicator_lb=service_btn_indicator, page=service_page))
service_btn.place(x=9, y=190, width=30, height=40)
service_btn_indicator = tk.Label(menu_bar_frame, bg=menu_bar_colour)
service_btn_indicator.place(x=3, y=190, width=3, height=40)

update_btn = tk.Button(menu_bar_frame, text="👤", font=("Arial", 14), bg=menu_bar_colour, bd=0, activebackground=menu_bar_colour, 
                        command=lambda: switch_indication(indicator_lb=update_btn_indicator, page=update_page))
update_btn.place(x=9, y=250, width=30, height=40)
update_btn_indicator = tk.Label(menu_bar_frame, bg=menu_bar_colour)
update_btn_indicator.place(x=3, y=250, width=3, height=40)

# Ajout de l'icône de profil initiale
profile_img = get_profile_image()
update_btn.configure(image=profile_img)
update_btn.image = profile_img

menu_bar_frame.pack(side=tk.LEFT, fill=tk.Y, pady=4, padx=3)
menu_bar_frame.configure(width=45)

root.mainloop()
