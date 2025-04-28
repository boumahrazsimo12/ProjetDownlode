import bcrypt

def hash_password(password):
    """Hacher le mot de passe"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(hashed_password, user_password):
    """Vérifier le mot de passe"""
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)
