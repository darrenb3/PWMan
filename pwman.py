import os
import random
import sqlite3
import string
from datetime import datetime

import PySimpleGUI as sg
from hashlib import sha256
from cryptography.hazmat.primitives import hashes

from crypto_funcs import crypto


class gui:  # Test class that creates a super basic gui based on simplepygui
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
        password = sg.popup_get_text("Please enter your password:", title="Login")
        digest = hashes.Hash(hashes.SHA256())
        digest.update(password.encode())
        password = str(digest.finalize().hex())
        row = self.cur.execute("SELECT password FROM password")
        hash_pass = row.fetchone()[0]  # Pulls hashed password hex from db
        while True:
            if hash_pass == password:
                sg.popup_auto_close(
                    "Password Correct", "Unlocking Database...", auto_close_duration=2
                )
                loggedin = 1
                break

            else:
                # need to look at using a flag variable or other method to stop all execution of the app after 3 attempts
                sg.popup("Incorrect Password. Please try again.")
                continue
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
            if (
                event == sg.WIN_CLOSED or event == "Cancel"
            ):  # if user closes window or clicks cancel
                break
            elif event == "-TABLE-":
                selected = [table[i] for i in values["-TABLE-"]]
            elif event == "New Item":
                self.new_item(hash_pass)
                table = self.db_fetch(hash_pass)
                window["-TABLE-"].update(values=table)
                window.refresh()
            elif event == "Update Item":
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
            elif event == "Refresh":
                table = self.db_fetch(hash_pass)
                window["-TABLE-"].update(values=table)
                window.refresh()
            elif event == "Delete":
                self.delete_item(selected[0][0])
                table = self.db_fetch(hash_pass)
                window["-TABLE-"].update(values=table)
                window.refresh()

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


# driver code
if __name__ == "__main__":
    gui = gui()
    gui.main()
