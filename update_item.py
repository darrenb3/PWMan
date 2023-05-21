import sqlite3
from datetime import datetime
from rich.console import Console

console = Console(highlight=False)


def update_item():
    item_name = console.input(
        "\nPlease enter the name of the item you want to update:\n")
    # Need to put error checking here that the record actually exists
    item_content = console.input(
        "\nPlease enter the new content of the item:\n")
    now = datetime.now().strftime('%H:%M:%S %m/%d/%Y')
#    console.print(now)
    data = [now, item_content, item_name]
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("UPDATE items SET date = ?, string = ? WHERE name LIKE ?", data)
    con.commit()
    con.close()
    return True
