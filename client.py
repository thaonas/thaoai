import tkinter as tk
import requests
import pyttsx3
import threading
import time
import json
import os
from datetime import datetime

# Chemin vers le fichier de configuration
CONFIG_FILE = "config.json"

# Charger la configuration
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # Valeurs par défaut
    return {
        "theme": "dark",
        "voice": {"gender": "default", "rate": 150, "volume": 0.8},
        "server": {"url": "http://192.168.1.51:5000/parle"},
        "assistant": {
            "auto_listen": false,
            "save_history": true,
            "use_audio_feedback": true,
            "temperature": 0.7,
            "max_tokens": 100
        }
    }

# Sauvegarder la configuration
def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

config = load_config()

print("🟢 Lancement du client...")

# Initialisation de la synthèse vocale
engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Appliquer la voix sélectionnée
selected_voice = config["voice"]["gender"]

def apply_voice():
    global engine
    engine.stop()
    engine = pyttsx3.init()
    for voice in voices:
        langs = voice.languages
        lang = langs[0] if langs else ""
        if isinstance(lang, bytes):
            lang = lang.decode()
        if "fr" in lang.lower():
            if selected_voice == "male":
                if "male" in voice.name.lower() or "homme" in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            elif selected_voice == "female":
                if "female" in voice.name.lower() or "feminine" in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
    engine.setProperty('rate', config["voice"]["rate"])
    engine.setProperty('volume', config["voice"]["volume"])

apply_voice()

loading = False
animation_ligne_index = None

fenetre = tk.Tk()
fenetre.title("Assistant Vocal")

texte_conversation = tk.Text(fenetre, height=20, width=60, wrap="word")
texte_conversation.pack(padx=10, pady=10, fill="both", expand=True)

cadre_input = tk.Frame(fenetre)
cadre_input.pack(fill="x", padx=10, pady=(0, 5))

entree = tk.Entry(cadre_input, width=50)
entree.pack(side="left", fill="x", expand=True)

bouton_envoyer = tk.Button(cadre_input, text="Envoyer")
bouton_envoyer.pack(side="left", padx=5)

case_sombre = tk.BooleanVar(value=config.get("theme", "dark") == "dark")

def basculer_theme():
    mode_sombre = case_sombre.get()
    config["theme"] = "dark" if mode_sombre else "light"
    save_config(config)
    appliquer_theme()

def appliquer_theme():
    mode_sombre = theme_var.get()
    bg = "#1e1e1e" if mode_sombre else "#f0f0f0"
    fg = "#dcdcdc" if mode_sombre else "#000000"
    entry_bg = "#2e2e2e" if mode_sombre else "#ffffff"
    bouton_bg = "#444" if mode_sombre else "#e0e0e0"

    fenetre.configure(bg=bg)
    cadre_input.configure(bg=bg)
    texte_conversation.configure(bg=bg, fg=fg, insertbackground=fg)
    entree.configure(bg=entry_bg, fg=fg, insertbackground=fg)
    bouton_envoyer.configure(bg=bouton_bg, fg="white" if mode_sombre else "black")
    case_sombre.set(mode_sombre)

theme_var = tk.BooleanVar(value=(config["theme"] == "dark"))
appliquer_theme()

# Création du menu
menubar = tk.Menu(fenetre)
menu_parametres = tk.Menu(menubar, tearoff=0)
menu_themes = tk.Menu(menu_parametres, tearoff=0)
menu_voix = tk.Menu(menu_parametres, tearoff=0)

# Menu Thèmes
menu_themes.add_radiobutton(label="Clair", variable=theme_var, value=False, command=basculer_theme)
menu_themes.add_radiobutton(label="Sombre", variable=theme_var, value=True, command=basculer_theme)

# Menu Voix
def set_voice(gender):
    global selected_voice
    selected_voice = gender
    config["voice"]["gender"] = gender
    save_config(config)
    apply_voice()

menu_voix.add_command(label="Voix masculine", command=lambda: set_voice("male"))
menu_voix.add_command(label="Voix féminine", command=lambda: set_voice("female"))
menu_voix.add_command(label="Voix par défaut", command=lambda: set_voice("default"))

# Intégration au menu principal
menu_parametres.add_cascade(label="Thème", menu=menu_themes)
menu_parametres.add_cascade(label="Voix", menu=menu_voix)
menu_parametres.add_separator()
menu_parametres.add_checkbutton(label="Feedback vocal", onvalue=True, offvalue=False,
                                variable=tk.BooleanVar(value=config["assistant"]["use_audio_feedback"]),
                                command=lambda: toggle_option("use_audio_feedback"))
menu_parametres.add_checkbutton(label="Sauvegarder l'historique", onvalue=True, offvalue=False,
                                variable=tk.BooleanVar(value=config["assistant"]["save_history"]),
                                command=lambda: toggle_option("save_history"))
menu_parametres.add_checkbutton(label="Auto-écoute", onvalue=True, offvalue=False,
                                variable=tk.BooleanVar(value=config["assistant"].get("auto_listen", False)),
                                command=lambda: toggle_option("auto_listen"))

def toggle_option(option_name):
    config["assistant"][option_name] = not config["assistant"].get(option_name, False)
    save_config(config)

menubar.add_cascade(label="Paramètres", menu=menu_parametres)
fenetre.config(menu=menubar)

def afficher_animation():
    i = 0
    frames = ["|", "/", "-", "\\"]  # Animation rotative simple
    while loading:
        time.sleep(0.2)
        frame = frames[i % len(frames)]
        try:
            texte_conversation.delete(animation_ligne_index, f"{animation_ligne_index} lineend")
            texte_conversation.insert(animation_ligne_index, f"Assistant : {frame}")
        except tk.TclError:
            pass
        texte_conversation.see(tk.END)
        i += 1

def parler_au_serveur(message):
    url = config["server"]["url"]
    try:
        response = requests.post(url, json={"message": message}, timeout=60)
        if response.status_code != 200:
            return f"Erreur serveur : {response.status_code}"
        return response.json().get("response", "Erreur de réponse.")
    except Exception as e:
        return f"Erreur : {e}"

def envoyer_message():
    global loading, animation_ligne_index
    message = entree.get()
    if not message.strip():
        return

    timestamp = datetime.now().strftime("[%H:%M:%S]")
    texte_conversation.insert(tk.END, f"{timestamp} Tu : {message}\n")
    animation_ligne_index = texte_conversation.index(tk.END)
    texte_conversation.insert(tk.END, "Assistant : ...\n")
    entree.delete(0, tk.END)

    def traiter():
        global loading
        loading = True
        animation_thread = threading.Thread(target=afficher_animation)
        animation_thread.start()

        reponse = parler_au_serveur(message)

        loading = False
        animation_thread.join()
        texte_conversation.delete(animation_ligne_index, f"{animation_ligne_index} lineend")

        horodatage = datetime.now().strftime("[%H:%M:%S]")
        texte_conversation.insert(animation_ligne_index, f"Assistant : {reponse}\n")
        if "Erreur" not in reponse and config["assistant"]["use_audio_feedback"]:
            engine.say(reponse)
        elif "Erreur" in reponse and config["assistant"]["use_audio_feedback"]:
            engine.say("Désolé, je n’ai pas pu me connecter au serveur.")
        engine.runAndWait()

    threading.Thread(target=traiter).start()

bouton_envoyer.configure(command=envoyer_message)
fenetre.bind("<Return>", lambda e: envoyer_message())

try:
    fenetre.mainloop()
except Exception as e:
    print(f"❌ Erreur : {e}")
    input("Appuie sur Entrée pour quitter…")