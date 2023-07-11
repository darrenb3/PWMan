# This is the driver code for the cli password manager app
# TODO: refactor driver code into class
from rich.console import Console
from dotenv import load_dotenv
import os
import sqlite3
import string
import random
import cryptography
import create_item
import list_items
import update_item
import delete_item

if __name__ == "__main__":
    console = Console(highlight=False)
    console.print("Running the preflight check...")
    console.print("Checking for database...")
    db_present = os.path.exists("database.db")
    if db_present:  # Checking if database.db exits. If not creates db file and table
        console.print("Database present...")
        pass
    else:
        con = sqlite3.connect("database.db")
        cur = con.cursor()
        cur.execute("CREATE TABLE items(name, date, string)")
        con.close()
        console.print("Database created...")
    console.print("Checking for salt table")
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    row = cur.execute("SELECT name FROM sqlite_master WHERE name='salt'")
    salt_check = row.fetchone()
    print(salt_check)
    if salt_check == None:
        cur.execute("CREATE TABLE salt(salt)")
        salt = ''.join(random.choices(string.ascii_lowercase +
                                      string.digits, k=7))
        print(salt)
        cur.execute("INSERT INTO salt VALUES(?)", [salt])  # salt check creates
        con.close()
        console.print("Salt created...")
    else:
        con.close()
        console.print("Salt exists...")
    console.print("Preflight complete!\n")
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
            if create_item.new_item():
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
