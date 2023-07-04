import base64
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class crypto:
    def encrypt(self, plain_text, password):
        """Accepts utf8 plain text input and password and returns utf8 cipher text"""
        password = password.encode()
        salt = b"salt"  # need to create a way of creating a random salt at some point
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        f = Fernet(key)
        cipher_text = f.encrypt(plain_text.encode()).decode()
        return cipher_text

    def decrypt(self, cipher_text, password):
        """Accepts utf8 cipher text and password and return utf8 plain text """
        password = password.encode()
        salt = b"salt"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        f = Fernet(key)
        plain_text = f.decrypt(cipher_text).decode()
        return plain_text
