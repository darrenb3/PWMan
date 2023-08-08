from rich.console import Console
from rich.table import Table
from cryptography.hazmat.primitives import hashes
from datetime import datetime
from crypto_funcs import crypto
import os
import sqlite3
import string
import random


class pwman:
    console = Console(highlight=False)
    con = None
    cur = None
    crypto = crypto()

    def __init__(self):
        """Checks for presence of sqlite db file"""
        self.console.print("Checking for database...")
        db_present = os.path.isfile("database.db")
        print(db_present)
        if (
            db_present
        ):  # Checking if database.db exits. If not creates db file and table
            self.con = sqlite3.connect("database.db")
            self.cur = self.con.cursor()
            self.console.print("Database present...")
            pass
        else:
            self.con = sqlite3.connect("database.db")
            self.cur = self.con.cursor()
            self.cur.execute("CREATE TABLE items(name, date, string)")
            self.cur.execute("CREATE TABLE salt(salt)")
            self.cur.execute("CREATE TABLE password(password)")
            self.console.print("Database created...")
            # Checks for presence of salt in the database
            self.console.print("Checking for salt presence")
            row = self.cur.execute("SELECT salt FROM salt")
            salt_check = row.fetchone()
            if salt_check == None:
                salt = [
                    "".join(random.choices(string.ascii_lowercase + string.digits, k=7))
                ]
                self.cur.execute(
                    "INSERT INTO salt VALUES(?)", salt
                )  # creates and inserts salt into its own table
                self.con.commit()
                self.console.print("Salt created...")
            else:
                self.console.print("Salt exists...")
            # Checks for presence of password table. If not present prompts user to create their password and saves it
            self.console.print("Checking for password presence")
            row = self.cur.execute("SELECT password FROM password")
            salt_check = row.fetchone()
            if salt_check == None:
                password = self.console.input("\nPlease enter a new password.\n")
                digest = hashes.Hash(hashes.SHA256())
                digest.update(password.encode())
                password = [str(digest.finalize())]
                self.cur.execute(
                    "INSERT INTO password VALUES(?)", password
                )  # creates and inserts password hash into its own table
                self.con.commit()
                self.console.print("Password created...")
            else:
                self.console.print("Password exists...")

    def login(self):
        """Checks that password is correct and returns it for use with crypto funcs"""
        password = self.console.input("\nPlease enter your password...\n")
        digest = hashes.Hash(hashes.SHA256())
        digest.update(password.encode())
        password = str(digest.finalize())
        row = self.cur.execute("SELECT password FROM password")
        hash_pass = row.fetchone()
        while True:
            if hash_pass[0] == password:
                self.console.print("Password Correct!")
                return hash_pass

            else:
                # need to look at using a flag variable or other method to stop all execution of the app after 3 attempts
                self.console.print("Password Incorrect! Please try again.")
                break

    def new_item(self, password):
        name = self.console.input("\nPlease enter a name for your item:\n")
        self.console.print("")
        content = self.console.input("\nPlease enter the content of your item:\n")
        # need to have driver code ask for password and pass into this function.
        content = self.crypto.encrypt(content, password)
        self.console.print("")
        now = datetime.now().strftime("%H:%M:%S %m/%d/%Y")
        data = [name, now, content]
        self.cur.execute("INSERT INTO items VALUES(?,?,?)", data)
        self.con.commit()
        self.console.print("\nItem created successfully\n")

    def update_item(self, password):
        item_name = self.console.input(
            "\nPlease enter the name of the item you want to update:\n"
        )
        # Need to put error checking here that the record actually exists
        item_content = self.console.input(
            "\nPlease enter the new content of the item:\n"
        )
        now = datetime.now().strftime("%H:%M:%S %m/%d/%Y")
        item_content = self.crypto.encrypt(item_content, password)
        data = [now, item_content, item_name]
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        cur.execute("UPDATE items SET date = ?, string = ? WHERE name LIKE ?", data)
        con.commit()
        con.close()
        self.console.print("\nItem has been updated successfully\n")

    def list_item(self, password):
        user_input = input("\nPlease enter the name of the item you want to read:\n")
        row = self.cur.execute(
            "SELECT name, date,string from items WHERE name LIKE ?", [user_input]
        )
        result = row.fetchone()
        self.console.print(
            f"\n[bold underline #ffa6c9]{result[0]}[/bold underline #ffa6c9]\nLast updated at {result[1]}:\n"
        )
        self.console.print(self.crypto.decrypt(f"{result[2]}\n", password))

    def list_all_items(self):
        table = Table(title="Current Items")
        table.add_column("Name")  # style="pink"
        table.add_column("Last Edited")
        table.add_column("Contents")
        for row in self.cur.execute("SELECT name, date, string FROM items"):
            table.add_row(
                f"{row[0]}", f"{row[1]}", self.crypto.decrypt(f"{row[2]}", password)
            )
        self.console = Console(highlight=False)
        self.console.print(table)

    def delete_item(self):
        item_name = self.console.input(
            "\nPlease enter the name of the item you want to delete:\n"
        )
        # Need to put error checking here that the record actually exists
        while True:
            confirmation = self.console.input(
                f"\nAre you sure that you want to delete {item_name}? [bold red]This action is irreversible[/bold red]. (y/[bold]N[/bold]):\n"
            )
            if confirmation.lower() == "n":
                break
            elif confirmation.lower() == "y":
                self.cur.execute("DELETE FROM items WHERE name = ?", [item_name])
                self.con.commit()
                return True
            else:
                self.console.print("Please enter a valid confirmation.")


# driver code
if __name__ == "__main__":
    console = Console(highlight=False)
    console.print("Running the preflight check...")
    pwman = pwman()
    console.print("Preflight complete!\n")
    password = str(pwman.login())
    console.print("\nWelcome to")  # Generated with TextKool using Big font
    logo = """
  _______          ____  __             
 |  __ \ \        / /  \/  |            
 | |__) \ \  /\  / /| \  / | __ _ _ __  
 |  ___/ \ \/  \/ / | |\/| |/ _` | '_ \ 
 | |      \  /\  /  | |  | | (_| | | | |
 |_|       \/  \/   |_|  |_|\__,_|_| |_| 
"""
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
            "\nPlease enter a command. For a list of commands use [bold]help[/bold]:\n"
        )
        match user_input:
            case "exit":
                console.print("\nThank you for using Password Manager\n\nExiting...\n")
                break
            case "new":
                pwman.new_item(password)
            case "list -a":
                pwman.list_all_items()
            case "list":
                pwman.list_item(password)
            case "update":
                pwman.update_item(password)
            case "delete":
                d = pwman.delete_item()
                if d.delete_item():
                    console.print("\nThe item was successfully deleted\n")
                else:
                    console.print("\nNo items were deleted\n")
            case _:
                console.print(help_options)
