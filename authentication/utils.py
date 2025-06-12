from cryptography.fernet import Fernet
import base64
from django.conf import settings

# Générer une clé à partir du SECRET_KEY
key = base64.urlsafe_b64encode(settings.SECRET_KEY[:32].encode())
fernet = Fernet(key)

def encrypt_password(password):
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(token):
    try:
        return fernet.decrypt(token.encode()).decode()
    except:
        return ''