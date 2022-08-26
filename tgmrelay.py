import string

from pyrogram import Client, filters
from datetime import datetime
import sqlite3
import json, string
import os
import requests
import pprint
from weather_config import openweather

config = {
    "name": "tgmrelay",
    "messages": "messages.db",
    "api_id": 2843096,
    "api_hash": "b3fe86810322a24fc277cde79cd318ca",
    "source_chat_id": -1001461338272,
    "target_chat_id": -1001597517662,
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
            print(result)
            return bool(len(result))

    def add(self, target, source, message: int, text: str):
        with self.connection:
            return self.cursor.execute("INSERT INTO messages VALUES (?,?,?,?);", (target, source, message, text))

    def close(self):
        self.connection.close()

app = Client(config["name"], config["api_id"], config["api_hash"], system_version='Arch', no_updates=False, hide_password=True)
messages = Messages(config["messages"])
with app:
    print(app.export_session_string())


@app.on_message(filters.chat(config["source_chat_id"]))
async def filterpurge(client, message):
    if {i.lower().translate(str.maketrans("", "", string.punctuation)) for i in message.text.split(' ')}\
        .intersection(set(json.load(open('keywords.json')))) != set():
        await app.forward_messages(config["target_chat_id"], config["source_chat_id"], message.id, message.text)
        print(message)
        # store message in the database
        await messages.add(config["target_chat_id"], message.chat.id, message.id, message.text)



@app.on_message(filters.chat(config["source_chat_id"]))
def get_post(client, message):
    print('it works')
    # relay only new messages, for this purpose we store all past messages in db
    if not messages.exists(config["target_chat_id"], message.id, message.text):
        # relay message to target chat
        app.forward_messages(config["target_chat_id"], config["source_chat_id"], message.id, message.text)
        # store message in the database
        messages.add(config["target_chat_id"], message.chat.id, message.id, message.text)
        
###def print_copy_text(message.text, message.copy)
def weather(openweather):
    try:
        r = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?lat=33.44&lon=-94.04&appid={openweather}"
        )

        data = r.json()
        print(r)

        city = data['Kursk']
    except Exception as ex:
        print(ex)
        print('Hiiiiiiiiii')


weather(openweather)

def main():
    pass

    print(datetime.today().strftime(f'%H:%M:%S | Started.'))
    app.run()
    #get_post(app, 'message')



if __name__ == '__main__':
    main()
