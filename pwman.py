import sqlite3
from datetime import datetime

import PySimpleGUI as sg
from cryptography.hazmat.primitives import hashes

from crypto_funcs import crypto


class gui:  # Test class that creates a super basic gui based on simplepygui
    con = None
    cur = None
    crypto = crypto()

    def main(self):
        sg.theme("SystemDefault")  # Add a touch of color
        # Login variable to start the log in process for the loop
        self.con = sqlite3.connect("database.db")
        self.cur = self.con.cursor()
        password = sg.popup_get_text("Please enter your password:", title="Login")
        digest = hashes.Hash(hashes.SHA256())
        digest.update(password.encode())
        password = str(digest.finalize())
        row = self.cur.execute("SELECT password FROM password")
        hash_pass = row.fetchone()
        while True:
            if hash_pass[0] == password:
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
                )
            ],
            [sg.Push(), sg.Button("New Item"), sg.Button("Refresh")],
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
            elif event == "New Item":
                self.new_item(hash_pass)
            elif event == "Refresh":
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
                    self.crypto.decrypt(f"{row[2]}", str(hash_pass)),
                ]
            )
        return table

    def new_item(self, hash_pass):
        name = sg.popup_get_text("Please enter a name for your item:")
        content = sg.popup_get_text("Please enter the content of your item:")
        content = self.crypto.encrypt(content, str(hash_pass))
        now = datetime.now().strftime("%H:%M:%S %m/%d/%Y")
        data = [name, now, content]
        self.cur.execute("INSERT INTO items VALUES(?,?,?)", data)
        self.con.commit()
        sg.popup_auto_close("created successfully")


# driver code
if __name__ == "__main__":
    gui = gui()
    gui.main()
