import tkinter as tk
import requests
import pyttsx3
import threading
import time
from datetime import datetime

print("🟢 Lancement du client...")

# Initialisation de la synthèse vocale
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    langs = voice.languages
    if langs:
        lang = langs[0]
        if isinstance(lang, bytes):
            lang = lang.decode()
        if "fr" in lang.lower():
            engine.setProperty('voice', voice.id)
            break
engine.setProperty('rate', 150)

# Variables globales pour l'animation
loading = False
animation_ligne_index = None

# Création de l'interface Tkinter
fenetre = tk.Tk()
fenetre.title("Assistant Vocal IA - Connexion Locale")

texte_conversation = tk.Text(fenetre, height=20, wrap="word")
texte_conversation.pack(padx=10, pady=10, fill="both", expand=True)

cadre_input = tk.Frame(fenetre)
cadre_input.pack(fill="x", padx=10, pady=(0, 5))

entree = tk.Entry(cadre_input, width=50)
entree.pack(side="left", fill="x", expand=True)

bouton_envoyer = tk.Button(cadre_input, text="Envoyer")
bouton_envoyer.pack(side="left", padx=5)

theme_var = tk.BooleanVar(value=True)
case_sombre = tk.Checkbutton(fenetre, text="Mode sombre", variable=theme_var)
case_sombre.pack(anchor="w", padx=10)

# bouton effacer la conversation
def effacer_conversation():
    texte_conversation.delete(1.0, tk.END)

bouton_effacer = tk.Button(cadre_input, text="Effacer", command=effacer_conversation)
bouton_effacer.pack(side="left", padx=5)

# Fonction d'application du thème
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
    case_sombre.configure(bg=bg, fg=fg, activebackground=bg, selectcolor=bg)

appliquer_theme()

# URL du serveur Ubuntu
SERVER_URL = "http://192.168.1.51:5000/parle"

def parler_au_serveur(message):
    try:
        response = requests.post(SERVER_URL, json={"message": message}, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "Erreur de réponse.")
    except requests.exceptions.Timeout:
        return "Erreur : Timeout lors de la connexion au serveur."
    except requests.exceptions.ConnectionError:
        return "Erreur : Impossible de se connecter au serveur."
    except Exception as e:
        return f"Erreur inconnue : {e}"

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
        if "Erreur" not in reponse:
            engine.say(reponse)
        else:
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