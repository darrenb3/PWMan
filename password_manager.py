# This is the driver code for the cli password manager app
# TODO: refactor driver code into class
from rich.console import Console
from dotenv import load_dotenv
from cryptography.hazmat.primitives import hashes
import os
import sqlite3
import string
import random
import cryptography
import create_item
import list_items
import update_item
import delete_item


class pwman:
    console = Console(highlight=False)

    def dbcheck(self):
        """Checks for presence of sqlite db file"""
        console.print("Checking for database...")
        db_present = os.path.exists("database.db")
        if db_present:  # Checking if database.db exits. If not creates db file and table
            console.print("Database present...")
            pass
        else:
            con = sqlite3.connect("database.db")
            cur = con.cursor()
            cur.execute("CREATE TABLE items(name, date, string)")
            cur.execute("CREATE TABLE salt(salt)")
            cur.execute("CREATE TABLE password(password)")
            con.close()
            console.print("Database created...")

    def saltcheck(self):
        """Checks for presence of salt in the database"""
        console.print("Checking for salt presence")
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        row = cur.execute("SELECT salt FROM salt")
        salt_check = row.fetchone()
        if salt_check == None:
            salt = [''.join(random.choices(string.ascii_lowercase +
                                           string.digits, k=7))]
            cur.execute("INSERT INTO salt VALUES(?)",
                        salt)  # creates and inserts salt into its own table
            con.commit()
            con.close()
            console.print("Salt created...")
        else:
            con.close()
            console.print("Salt exists...")
    def passcheck(self):
        """Checks for presence of password table. If not present prompts user to create their password and saves it"""
        console.print("Checking for password presence")
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        row = cur.execute("SELECT password FROM password")
        salt_check = row.fetchone()
        if salt_check == None:
            password = console.input("Please enter a new password.\n")
            digest = hashes.Hash(hashes.SHA256())
            digest.update(password.encode())
            password = [str(digest.finalize())]
            cur.execute("INSERT INTO password VALUES(?)",
                        password)  # creates and inserts password hash into its own table
            con.commit()
            con.close()
            console.print("Password created...")
        else:
            con.close()
            console.print("Password exists...")

    def login(self):
        """Checks that password is correct and returns it for use with crypto funcs"""
        password = console.input("Please enter your password...\n")
        digest = hashes.Hash(hashes.SHA256())
        digest.update(password.encode())
        password = str(digest.finalize())
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        row = cur.execute("SELECT password FROM password")
        hash_pass = row.fetchone()
        while True:
            if hash_pass[0] == password:
                console.print("Password Correct!")
                break
            else:
                console.print("Password Incorrect! Please try again.")
                break


if __name__ == "__main__":
    console = Console(highlight=False)
    pwman = pwman()
    console.print("Running the preflight check...")
    pwman.dbcheck()
    pwman.saltcheck()
    pwman.passcheck()
    console.print("Preflight complete!\n")
    password = pwman.login()
    console.print("\nWelcome to")  # Generated with TextKool using Big font
    logo = """  _____                                    _   __  __                                   
 |  __ \                                  | | |  \/  |                                  
 | |__) |_ _ ___ _____      _____  _ __ __| | | \  / | __ _ _ __   __ _  __ _  ___ _ __ 
 |  ___/ _` / __/ __\ \ /\ / / _ \| '__/ _` | | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__|
 | |  | (_| \__ \__ \\ V  V / (_) | | | (_| | | |  | | (_| | | | | (_| | (_| |  __/ |   
 |_|   \__,_|___/___/ \_/\_/ \___/|_|  \__,_| |_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|   
                                                                         __/ |          
                                                                        |___/           \n"""
    console.print(logo, style="#ffa6c9")
    while True:
        help_options = """\nTo enter a new item please type new
To list all item please type list -a
To list a single item please type list
To update a item please type update
To delete a item please type delete
To exit the app please type exit
"""
        user_input = console.input(
            "\nPlease enter a command. For a list of commands use [bold]help[/bold]:\n")
        if user_input == "exit":
            console.print(
                "\nThank you for using Password Manager\n\nExiting...\n")
            break
        elif user_input == "new":
            if create_item.new_item(password):
                console.print("\nitem created successfully\n")
        elif user_input == "list -a":
            list_items.list_all_items()
        elif user_input == "list":
            list_items.list_item()
        elif user_input == "update":
            if update_item.update_item():
                console.print("\nItem has been updated successfully\n")
        elif user_input == "delete":
            if delete_item.delete_item():
                console.print("\nThe item was successfully deleted\n")
            else:
                console.print("\nNo items were deleted\n")
        else:
            console.print(help_options)
