# -*- coding: utf-8 -*-
import os
import datetime

def save_conversation(user_input, bot_response):
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/logs.txt", "a", encoding="utf-8") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp}\n")
            f.write(f"Utilisateur : {user_input}\n")
            f.write(f"Assistant  : {bot_response}\n\n")
    except Exception as e:
        print(f"❌ Erreur lors de l'enregistrement : {e}")