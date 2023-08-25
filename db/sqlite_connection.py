import sqlite3

from models import UserClient, User


class Database:
    def __init__(self, db_file) -> None:

        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def cbdt(self):
        with self.connection:
            create = """ CREATE TABLE IF NOT EXISTS Contacts
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL UNIQUE ON CONFLICT IGNORE,
                    full_name TEXT,
                    phone TEXT,
                    username TEXT);"""
            self.cursor.executescript(create)

    def add_contact(self, telegram_id, full_name, phone, username):
        with self.connection:
            self.cursor.execute(
                f"INSERT OR IGNORE INTO Contacts(telegram_id,full_name,phone, username) VALUES(?,?,?,?)", (telegram_id, full_name, phone, username))

    def get_user_id_by_phone(self, phone):
        with self.connection:
            c = self.cursor.execute(
                "SELECT telegram_id FROM Contacts WHERE phone=?", (phone,))
            rows = c.fetchone()
            return rows


if __name__ == "__main__":
    a = Database("FB.db")
    a.cbdt()
