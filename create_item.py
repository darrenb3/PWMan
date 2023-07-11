# contains all functions required to create a new item in the database
import sqlite3
from datetime import datetime
from rich.console import Console
from crypto_funcs import crypto

console = Console(highlight=False)
crypto = crypto()

def new_item(password):
    name = console.input("\nPlease enter a name for your item:\n")
    console.print("")
    content = console.input("\nPlease enter the content of your item:\n")
    content = crypto.encrypt(content,password) # need to have driver code ask for password and pass into this function.
    console.print("")
    now = datetime.now().strftime('%H:%M:%S %m/%d/%Y')
    data = [name, now, content]
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO items VALUES(?,?,?)", data)
    con.commit()
    con.close()
    return True
