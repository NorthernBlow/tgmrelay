from pyrogram import Client, filters
from datetime import datetime
import sqlite3
import json

config = {
    "name": "tgm_relay",
    "messages": "messages.db",
    "api_id": "2843096",
    "api_hash": "b3fe86810322a24fc277cde79cd318ca",
    "source_chat_id": -1001442825795,
    "target_chat_id": -1001245620542,
}

class Messages:
    def __init__(self, database):
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()
        with self.connection:
            self.cursor.execute(
                "CREATE TABLE IF NOT EXISTS messages(target INTEGER, source INTEGER, message INTEGER, text VARCHAR(4096));")

    def exists(self, target, source, message: int):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM messages WHERE target=? AND source=? AND message=?;",
                                         (target, source, message)).fetchall()
            return bool(len(result))

    def add(self, target, source, message: int, text: str):
        with self.connection:
            return self.cursor.execute("INSERT INTO messages VALUES (?,?,?,?);", (target, source, message, text))

    def close(self):
        self.connection.close()

app = Client(config["name"], config["api_id"], config["api_hash"],)
messages = Messages(config["messages"])
with app:
    print(app.export_session_string())


@app.on_message(filters.chat(config["source_chat_id"]))
def get_post(client, message):
    # relay only new messages, for this purpose we store all past messages in db
    if not messages.exists(config["target_chat_id"], message.chat.id, message.message_id):
        # relay message to target chat
        app.forward_message(config["target_chat_id"], message.chat.id, message.message_id, message.copy)
        # store message in the database
        messages.add(config["target_chat_id"], message.chat.id, message.message_id, message.text)


def main():
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except OSError:
        print("config.json not found")
        pass

    print(datetime.today().strftime(f'%H:%M:%S | Started.'))
    app.run()


if __name__ == '__main__':
    main()
