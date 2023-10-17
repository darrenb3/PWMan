import argparse
import os
import random
import sqlite3
import string
from datetime import datetime

import PySimpleGUI as sg
from cryptography.hazmat.primitives import hashes
from rich.console import Console
from rich.table import Table

from crypto_funcs import crypto


class gui:  # GUI class implemented with pysimplegui. Responsible for main gui window and all functions.
    con = None
    cur = None
    crypto = crypto()

    def __init__(
        self,
    ):  # This initiates the class and will perform a basic check for the db file. If it is not present then it will prompt the user to create it
        sg.theme("SystemDefault")  # Add a touch of color
        db_present = os.path.isfile("database.db")
        if db_present:
            self.con = sqlite3.connect("database.db")
            self.cur = self.con.cursor()
        elif not db_present:
            self.con = sqlite3.connect(
                "database.db"
            )  # Calling connection will create the base DB file
            self.cur = self.con.cursor()
            # Creating DB schema
            self.cur.execute("CREATE TABLE items(name, date, string)")
            self.cur.execute("CREATE TABLE salt(salt)")
            self.cur.execute("CREATE TABLE password(password)")
            salt = [
                "".join(random.choices(string.ascii_lowercase + string.digits, k=7))
            ]
            self.cur.execute(
                "INSERT INTO salt VALUES(?)", salt
            )  # creates and inserts salt into its own table
            password = sg.popup_get_text(
                "Please enter the password you would like to use:",
                title="First time setup",
            )
            digest = hashes.Hash(hashes.SHA256())
            digest.update(password.encode())
            password = [str(digest.finalize().hex())]
            self.cur.execute(
                "INSERT INTO password VALUES(?)", password
            )  # creates and inserts password hash as a hex string into its own table
            self.con.commit()

    def main(self):
        row = self.cur.execute("SELECT password FROM password")
        hash_pass = row.fetchone()[0]  # Pulls hashed password hex from db
        while True:
            password = sg.popup_get_text("Please enter your password:", title="Login")
            digest = hashes.Hash(hashes.SHA256())
            digest.update(password.encode())
            password = str(digest.finalize().hex())
            if hash_pass == password:
                sg.popup_auto_close(
                    "Password Correct", "Unlocking Database...", auto_close_duration=2
                )
                loggedin = 1
                break

            else:
                # need to look at using a flag variable or other method to stop all execution of the app after 3 attempts
                sg.popup("Incorrect Password. Please try again.")
                pass
        # All layouts
        table = self.db_fetch(hash_pass)
        columns = ["Name", "Last Edited", "Content"]

        layout_main = [
            [sg.Text("Welcome to PWMan")],
            [
                sg.Table(
                    values=table,
                    headings=columns,
                    auto_size_columns=True,
                    justification="center",
                    key="-TABLE-",
                    expand_x=True,
                    expand_y=True,
                    enable_events=True,
                )
            ],
            [
                sg.Push(),
                sg.Button("New Item"),
                sg.Button("Update Item"),
                sg.Button("Refresh"),
                sg.Button("Delete", button_color=("white", "maroon")),
            ],
        ]

        # Create the Window
        window = sg.Window(
            "PWMan", layout_main, size=(700, 300), resizable=True, finalize=True
        )

        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            event, values = window.read()
            match event:
                case sg.WIN_CLOSED:
                    break
                case "Cancel":
                    break
                case "-TABLE-":
                    selected = [table[i] for i in values["-TABLE-"]]
                case "New Item":
                    self.new_item(hash_pass)
                    table = self.db_fetch(hash_pass)
                    window["-TABLE-"].update(values=table)
                    window.refresh()
                case "Update Item":
                    try:
                        self.update_item(hash_pass, selected[0][0])
                        table = self.db_fetch(hash_pass)
                        window["-TABLE-"].update(values=table)
                        window.refresh()
                    except:
                        sg.popup_auto_close(
                            "Please select an item to edit",
                            auto_close_duration=2,
                            title="Error",
                        )
                case "Refresh":
                    table = self.db_fetch(hash_pass)
                    window["-TABLE-"].update(values=table)
                    window.refresh()
                case "Delete":
                    self.delete_item(selected[0][0])
                    table = self.db_fetch(hash_pass)
                    window["-TABLE-"].update(values=table)
                    window.refresh()
                case _:
                    pass
        window.close()

    def db_fetch(self, hash_pass):
        table = []
        for row in self.cur.execute("SELECT name, date, string FROM items"):
            table.append(
                [
                    f"{row[0]}",
                    f"{row[1]}",
                    self.crypto.decrypt(f"{row[2]}", hash_pass),
                ]
            )
        return table

    def new_item(self, hash_pass):
        name = sg.popup_get_text("Please enter a name for your item:")
        content = sg.popup_get_text("Please enter the content of your item:")
        content = self.crypto.encrypt(content, hash_pass)
        now = datetime.now().strftime("%H:%M:%S %m/%d/%Y")
        data = [name, now, content]
        self.cur.execute("INSERT INTO items VALUES(?,?,?)", data)
        self.con.commit()
        sg.popup_auto_close("created successfully")

    def update_item(self, hash_pass, item_name):
        item_content = sg.popup_get_text("Please enter the new content of your item:")
        item_content = self.crypto.encrypt(item_content, hash_pass)
        now = datetime.now().strftime("%H:%M:%S %m/%d/%Y")
        data = [now, item_content, item_name]
        self.cur.execute(
            "UPDATE items SET date = ?, string = ? WHERE name LIKE ?", data
        )
        self.con.commit()
        sg.popup_auto_close("Item updated successfully", auto_close_duration=2)

    def delete_item(self, item_name):
        confirmation = sg.popup_yes_no(
            f"are you sure you want to delete {item_name}? ", title="Confirmation"
        )
        if confirmation == "Yes":
            self.cur.execute("DELETE FROM items WHERE name = ?", [item_name])
            self.con.commit()
        elif confirmation == "No":
            pass


class tui:
    console = Console(highlight=False)
    con = None
    cur = None
    crypto = crypto()

    def __init__(self):
        console = Console(highlight=False)
        console.print("Running the preflight check...")
        self.preflight()
        console.print("Preflight complete!\n")
        password = self.login()
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
                    console.print(
                        "\nThank you for using Password Manager\n\nExiting...\n"
                    )
                    break
                case "new":
                    self.new_item(password)
                case "list -a":
                    self.list_all_items(password)
                case "list":
                    self.list_item(password)
                case "update":
                    self.update_item(password)
                case "delete":
                    d = self.delete_item()
                    if d.delete_item():
                        console.print("\nThe item was successfully deleted\n")
                    else:
                        console.print("\nNo items were deleted\n")
                case _:
                    console.print(help_options)

    def preflight(self):
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
        row = self.cur.execute("SELECT password FROM password")
        hash_pass = row.fetchone()[0]
        while True:
            password = self.console.input("\nPlease enter your password...\n")
            digest = hashes.Hash(hashes.SHA256())
            digest.update(password.encode())
            password = str(digest.finalize().hex())
            if hash_pass == password:
                self.console.print("Password Correct!")
                return hash_pass
            else:
                # need to look at using a flag variable or other method to stop all execution of the app after 3 attempts
                self.console.print("Password Incorrect! Please try again.")
                pass

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

    def list_all_items(self, password):
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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-ng",
        "--nogui",
        help="Will launch PWMan in a terminal text only mode",
        action="store_true",
    )
    args = parser.parse_args()
    if args.nogui:
        tui = tui()
    else:
        gui = gui()
        gui.main()
