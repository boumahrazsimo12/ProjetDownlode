from tkinter import *
from tkinter import messagebox
import pymongo
import json
import subprocess

# Connexion à MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["test"]
users_collection = db["users"]


# Création de la fenêtre principale (Login)
root = Tk()
root.title('Login')
root.geometry('925x500+300+200')
root.configure(bg='#fff')
root.resizable(False, False)

# Fonction pour gérer les placeholders
def on_enter(e, widget, default_text):
    if widget.get() == default_text:
        widget.delete(0, 'end')
        widget.config(fg='black')

def on_leave(e, widget, default_text):
    if widget.get() == '':
        widget.insert(0, default_text)
        widget.config(fg='gray')

# Fonction pour se connecter
import subprocess

def signin():
    username = user.get()
    password = code.get()

    user_data = users_collection.find_one({"username": username})

    if user_data and user_data["password"] == password:
        # 🟢 Stocker l'utilisateur connecté dans session.json
        with open("session.json", "w") as f:
            json.dump({"username": username}, f)

        root.destroy()  # Fermer la fenêtre de connexion
        subprocess.run(["python", "muliPagesWithYoutube.py"])  # Ouvrir l'application principale
    else:
        messagebox.showerror('Invalid', 'User not found or incorrect password')

# Fonction pour ouvrir la fenêtre d'inscription
def signup():
    root.withdraw()  # Cacher la fenêtre principale (Login)
    window = Toplevel(root)
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
                users_collection.insert_one({"username": username, "password": password})
                messagebox.showinfo('Signup', 'Successfully signed up')

                # Fermer Sign Up et réafficher Login
                window.destroy()
                root.deiconify()
        else:
            messagebox.showerror('Invalid', 'Both passwords should match')


    # img = PhotoImage(file="C:/Users/bouma/Downloads/images/login_image.png")
    # Label(window, image=img, border=0, bg='white').place(x=50, y=50) 

    frame = Frame(window, width=350, height=390, bg='#fff')
    frame.place(x=480, y=50)

    heading = Label(frame, text='Sign up', fg='#57a1f8', bg='white', font=('Microsoft YaHei UI Light', 23, 'bold'))
    heading.place(x=100, y=5)

    user_entry = Entry(frame, width=25, fg='gray', border=0, bg='white', font=('Microsoft YaHei UI Light', 11))
    user_entry.insert(0, 'Username')
    user_entry.bind("<FocusIn>", lambda e: on_enter(e, user_entry, 'Username'))
    user_entry.bind("<FocusOut>", lambda e: on_leave(e, user_entry, 'Username'))
    user_entry.place(x=30, y=80)
    Frame(frame, width=295, height=2, bg='black').place(x=25, y=107)

    code_entry = Entry(frame, width=25, fg='gray', border=0, bg='white', font=('Microsoft YaHei UI Light', 11))
    code_entry.insert(0, 'Password')
    code_entry.bind("<FocusIn>", lambda e: on_enter(e, code_entry, 'Password'))
    code_entry.bind("<FocusOut>", lambda e: on_leave(e, code_entry, 'Password'))
    code_entry.place(x=30, y=150)
    Frame(frame, width=295, height=2, bg='black').place(x=25, y=177)

    confirm_code_entry = Entry(frame, width=25, fg='gray', border=0, bg='white', font=('Microsoft YaHei UI Light', 11))
    confirm_code_entry.insert(0, 'Confirm Password')
    confirm_code_entry.bind("<FocusIn>", lambda e: on_enter(e, confirm_code_entry, 'Confirm Password'))
    confirm_code_entry.bind("<FocusOut>", lambda e: on_leave(e, confirm_code_entry, 'Confirm Password'))
    confirm_code_entry.place(x=30, y=220)
    Frame(frame, width=295, height=2, bg='black').place(x=25, y=247)

    Button(frame, width=39, pady=7, text='Sign up', bg='#57a1f8', fg='white', border=0, command=register).place(x=35, y=280)

    # Si l'utilisateur ferme la fenêtre d'inscription, on réaffiche Login
    window.protocol("WM_DELETE_WINDOW", lambda: (window.destroy(), root.deiconify()))

    window.mainloop()

# img = PhotoImage(file="C:/Users/bouma/Downloads/images/login_image.png")
# Label(root, image=img, bg='white').place(x=50, y=30)


# Interface de connexion
frame = Frame(root, width=350, height=350, bg='white')
frame.place(x=480, y=70)

heading = Label(frame, text='Sign in', fg='#57a1f8', bg='white', font=('Microsoft YaHei UI Light', 23, 'bold'))
heading.place(x=100, y=5)

user = Entry(frame, width=25, fg='gray', border=0, bg='white', font=('Microsoft YaHei UI Light', 11))
user.insert(0, 'Username')
user.bind('<FocusIn>', lambda e: on_enter(e, user, 'Username'))
user.bind('<FocusOut>', lambda e: on_leave(e, user, 'Username'))
user.place(x=30, y=80)
Frame(frame, width=295, height=2, bg='black').place(x=25, y=107)

code = Entry(frame, width=25, fg='gray', border=0, bg='white', font=('Microsoft YaHei UI Light', 11))
code.insert(0, 'Password')
code.bind('<FocusIn>', lambda e: on_enter(e, code, 'Password'))
code.bind('<FocusOut>', lambda e: on_leave(e, code, 'Password'))
code.place(x=30, y=150)
Frame(frame, width=295, height=2, bg='black').place(x=25, y=177)

Button(frame, width=39, pady=7, text='Sign in', bg='#57a1f8', fg='white', border=0, command=signin).place(x=35, y=204)
Label(frame, text="Don't have an account?", fg='black', bg='white', font=('Microsoft YaHei UI Light', 9)).place(x=75, y=270)

Button(frame, width=6, text='Sign up', border=0, bg='white', cursor='hand2', fg='#57a1f8', command=signup).place(x=215, y=270)

root.mainloop()
