import sqlite3
from rich.console import Console

console = Console(highlight=False)


def delete_item():
    item_name = console.input(
        "\nPlease enter the name of the item you want to delete:\n")
    # Need to put error checking here that the record actually exists
    while True:
        confirmation = console.input(
            f"\nAre you sure that you want to delete {item_name}? [bold red]This action is irreversible[/bold red]. (y/[bold]N[/bold]):\n")
        if confirmation.lower() == "n":
            break
        elif confirmation.lower() == "y":
            con = sqlite3.connect("database.db")
            cur = con.cursor()
            cur.execute("DELETE FROM items WHERE name = ?", [item_name])
            con.commit()
            return True
        else:
            console.print("Please enter a valid confirmation.")
