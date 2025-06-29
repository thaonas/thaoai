from flask import Flask, request, jsonify
from modules.conversion_engine import traiter_conversion
from modules.math_engine import evaluer_expression
from modules.clock_engine import traiter_horloge
from modules.weather_engine import traiter_meteo
from modules.electric_engine import traiter_electricite
from modules.chatbot import generate_response

app = Flask(__name__)

memoire = []

def charger_contexte():
    """Construit le prompt à partir de la mémoire"""
    contexte = ""
    for q_or_r, contenu in memoire[:-1]:
        if q_or_r == "Question":
            contexte += f"Question : {contenu}\n"
        else:
            contexte += f"Réponse : {contenu}\n"

    contexte += f"Question : {memoire[-1][1]}\nRéponse :"
    return contexte


@app.route("/parle", methods=["POST"])
def parler():
    data = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"response": "Tu n’as rien dit 😅"})

    # 1. Essayer les conversions unitaires
    try:
        reponse_conversion = traiter_conversion(message)
        if reponse_conversion and not reponse_conversion.startswith("❌"):
            return jsonify({"response": reponse_conversion})
    except Exception as e:
        print(f"[ERREUR] Module conversion_engine : {e}")

    # 2. Essayer les calculs mathématiques complexes
    try:
        reponse_math = evaluer_expression(message)
        if reponse_math:
            return jsonify({"response": reponse_math})
    except Exception as e:
        print(f"[ERREUR] Module math_engine : {e}")

    # 3. Essayer les fonctionnalités horloge / calendrier
    try:
        reponse_horloge = traiter_horloge(message)
        if reponse_horloge:
            return jsonify({"response": reponse_horloge})
    except Exception as e:
        print(f"[ERREUR] Module clock_engine : {e}")

    # 4. Essayer les fonctionnalités météo
    try:
        reponse_meteo = traiter_meteo(message)
        if reponse_meteo:
            return jsonify({"response": reponse_meteo})
    except Exception as e:
        print(f"[ERREUR] Module weather_engine : {e}")

    # 5. Essayer les fonctionnalités électroniques
    try:
        reponse_elec = traiter_electricite(message)
        if reponse_elec:
            return jsonify({"response": reponse_elec})
    except Exception as e:
        print(f"[ERREUR] Module electric_engine : {e}")

    # 6. Si aucun module ne répond, passer à l'IA
    memoire.append(("Question", message))
    if len(memoire) > 10:
        memoire.pop(0)

    contexte = charger_contexte()
    print(f"🧠 Contexte transmis :\n{contexte}")

    try:
        reponse = generate_response(contexte)
    except Exception as e:
        print(f"❌ Erreur modèle : {e}")
        reponse = "Désolé, je n’ai pas pu générer de réponse."

    if not reponse or reponse.strip() == "":
        reponse = "Je ne suis pas sûr de savoir répondre à cela. Peux-tu reformuler ?"

    memoire.append(("Réponse", reponse))
    if len(memoire) > 10:
        memoire.pop(0)

    return jsonify({"response": reponse})


if __name__ == "__main__":
    print("🚀 Serveur en cours de démarrage sur http://192.168.1.51:5000")
    app.run(host="192.168.1.51", port=5000, debug=False)