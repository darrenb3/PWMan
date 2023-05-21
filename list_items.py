# Contains all fucntions for listing items
import sqlite3
from rich.console import Console
from rich.table import Table


def list_all_items():
    table = Table(title="Current Items")
    table.add_column("Name")  # style="pink"
    table.add_column("Last Edited")
    table.add_column("Contents")
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    for row in cur.execute("SELECT name, date, string FROM items"):
        table.add_row(f"{row[0]}", f"{row[1]}", f"{row[2]}")
    console = Console(highlight=False)
    console.print(table)
    con.close()


def list_item():
    console = Console(highlight=False)
    user_input = input(
        "\nPlease enter the name of the item you want to read:\n")
    print("")
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    row = cur.execute(
        "SELECT name, date,string from items WHERE name LIKE ?", [user_input])
    result = row.fetchone()
    console.print(
        f"\n[bold underline #ffa6c9]{result[0]}[/bold underline #ffa6c9]\nLast updated at {result[1]}:\n")
    console.print(f"{result[2]}\n")
