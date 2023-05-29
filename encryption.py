import base64
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def encrypter(password: str, plain_text: str):
    """
    Encryptor takes a password and plain_text, then returns a ciphertext in base64
    :param password:
    :param plain_text:
    :return:
    """
    load_dotenv()
    salt = os.getenv("KEY").encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000
    )
    plain_text = plain_text.encode()
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    f = Fernet(key)
    cipher = f.encrypt(plain_text).decode()
    return cipher


def decrypter(password: str, cipher_text: str):
    """
    Encryptor take a password and ciphertext, then returns a plaintext in base64
    :param password:
    :param cipher_text:
    :return:
    """
    load_dotenv()
    salt = os.getenv("KEY").encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    f = Fernet(key)
    plain_text = f.decrypt(cipher_text.encode()).decode()
    return plain_text
