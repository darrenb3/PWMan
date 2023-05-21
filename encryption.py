import base64
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def encoder(password,plain_text): # takes password and the plaintext btyestream inputs and returns encrypted hash btyesteam
    load_dotenv()
    salt = os.getenv("KEY").encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    token = f.encrypt(plain_text).decode()
    return token


def decoder(password,cipher_text): # takes password and the ciphertext btyestream inputs and returns plain text
    load_dotenv()
    salt = os.getenv("KEY").encode()
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
