# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import re
import threading
import time
import pytz  # Pour le support des fuseaux horaires complets

# Modules personnalisés
try:
    from modules.conversion_engine import traiter_conversion
except Exception as e:
    print(f"[ERREUR] Impossible d'importer conversion_engine : {e}")

try:
    from modules.math_engine import evaluer_expression
except Exception as e:
    print(f"[ERREUR] Impossible d'importer math_engine : {e}")

try:
    from modules.clock_engine import traiter_horloge
except Exception as e:
    print(f"[ERREUR] Impossible d'importer clock_engine : {e}")

try:
    from modules.weather_engine import traiter_meteo
except Exception as e:
    print(f"[ERREUR] Impossible d'importer weather_engine : {e}")

try:
    from modules.electric_engine import traiter_electricite
except Exception as e:
    print(f"[ERREUR] Impossible d'importer electric_engine : {e}")

try:
    from modules.chatbot import generate_response
except Exception as e:
    print(f"[ERREUR] Impossible d'importer chatbot : {e}")

app = Flask(__name__)

# Mémoire conversationnelle (max 10 échanges)
memoire = []

# Verrou pour protéger l'accès au modèle IA
model_lock = threading.Lock()

# Décorateur de timeout global
def timeout(seconds):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = [TimeoutError(f"⏰ Temps dépassé ({seconds}s)")]
            def run_func():
                try:
                    with model_lock:
                        result[0] = func(*args, **kwargs)
                except Exception as e:
                    result[0] = str(e)

            thread = threading.Thread(target=run_func)
            thread.start()
            thread.join(timeout=seconds)

            if thread.is_alive():
                print("❌ Requête trop longue → arrêt forcé.")
                return "Désolé, je prends trop de temps à répondre."

            return result[0]
        return wrapper
    return decorator


@timeout(60)
def generate_response_with_timeout(contexte):
    """Génère une réponse en utilisant le modèle IA local"""
    return generate_response(contexte)


@app.route("/parle", methods=["POST"])
def parler():
    data = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"response": "Tu n’as rien dit 😅"})

    # Nettoyage basique du message
    message_nettoye = message.lower().replace("donne-moi", "donne").replace("converti", "convertir")
    message_nettoye = message_nettoye.replace("temp", "temps").replace("méteo", "météo")
    message_nettoye = re.sub(r"[^\w\s]", "", message_nettoye).strip()

    print(f"🔍 Message reçu : {message}")
    print(f"🧹 Nettoyé : {message_nettoye}")

    # Essayer les modules en priorité
    module_tests = [
        ("conversion", traiter_conversion),
        ("math", evaluer_expression),
        ("horloge", traiter_horloge),
        ("météo", traiter_meteo),
        ("électricité", traiter_electricite)
    ]

    for name, func in module_tests:
        try:
            print(f"🧪 Test module {name} avec : '{message_nettoye}'")
            response = func(message_nettoye)
            if response and not response.startswith("Je ne suis pas sûr"):
                print(f"[{name}] ✅ Réponse trouvée : {response}")
                return jsonify({"response": response})
            else:
                print(f"[{name}] ❌ Aucune réponse utile")
        except Exception as e:
            print(f"[ERREUR] Module {name} a planté : {e}")

    # Si personne ne répond, passer à l'IA
    memoire.append(("Question", message))
    if len(memoire) > 10:
        memoire.pop(0)

    # Construit le contexte conversationnel
    contexte = ""
    for q_or_r, contenu in memoire[:-1]:
        if q_or_r == "Question":
            contexte += f"Question : {contenu}\n"
        else:
            contexte += f"Réponse : {contenu}\n"

    contexte += f"Question : {memoire[-1][1]}\nRéponse :"
    print(f"🧠 Contexte transmis :\n{contexte}")

    try:
        reponse = generate_response_with_timeout(contexte)
    except TimeoutError:
        reponse = "Désolé, je prends trop de temps à répondre."
    except Exception as e:
        print(f"❌ Erreur lors de la génération : {e}")
        reponse = None

    if not reponse or reponse.strip() == "":
        reponse = "Je ne comprends pas encore cette demande. Peux-tu reformuler ?"

    memoire.append(("Réponse", reponse))
    if len(memoire) > 10:
        memoire.pop(0)

    return jsonify({"response": reponse})


if __name__ == "__main__":
    print("🚀 Démarrage du serveur sur http://192.168.1.51:5000")
    app.run(host="192.168.1.51", port=5000, debug=True)