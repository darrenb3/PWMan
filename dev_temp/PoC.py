import base64
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def encoder():
    password = input('Please enter your password: ').encode()
    salt = b"salt"
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    token = f.encrypt(input("Please enter your message: ").encode())
    return token


def decoder(message):
    password = input('Please enter your password: ').encode()
    salt = b"salt"
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    decoded_message = f.decrypt(message)
    return decoded_message


if __name__ == "__main__":
    message = ""
    while True:
        user_input = input("Please input a command: ")
        if user_input == "encode":
            message = encoder()
            print(message)
        elif user_input == "decode":
            print(message)
            print(decoder(message))
        elif user_input == "exit":
            break
