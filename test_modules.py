"""
Script de test pour valider les différents modules de l'assistant.
"""

import requests

SERVER_URL = "http://192.168.1.51:5000/parle"


def tester_requete(message):
    """Envoie une requête au serveur et retourne la réponse"""
    try:
        response = requests.post(SERVER_URL, json={"message": message}, timeout=10)
        if response.status_code == 200:
            return response.json().get("response", "❌ Aucune réponse")
        else:
            return f"❌ Erreur HTTP {response.status_code}"
    except requests.exceptions.Timeout:
        return "⏰ Timeout"
    except Exception as e:
        return f"❌ Erreur réseau : {e}"


def run_tests():
    print("🧪 Démarrage des tests...\n")

    tests = {
        "Conversion simple": "150 cm en m",
        "Conversion complexe": "3.5 tonnes en kg",
        "Conversion temporelle": "2h30 en secondes",
        "Conversion incompatible": "5 km en pouces",
        "Calcul simple": "2 + 3 * 4",
        "Calcul complexe": "sqrt(2)+pi/2",
        "Calcul factorielle": "factorial(5)",
        "Calcul parenthèses": "(2+3)**2",
        "Heure actuelle": "Quelle heure est-il ?",
        "Heure à Paris": "Donne-moi l'heure à Meaux",
        "Heure à Tokyo": "Il est quelle heure à Tokyo ?",
        "Date actuelle": "Donne-moi la date",
        "Calcul durée": "Calcule 5 jours depuis aujourd'hui",
        "Météo à Paris": "Quel temps fait-il à Meaux ?",
        "Météo à Londres": "Est-ce qu'il pleut à Londres ?",
        "Météo à Tokyo": "Donne-moi la météo à Tokyo",
        "Loi d'Ohm U": "Calcule U avec R=10Ω et I=2A",
        "Loi d'Ohm R": "Donne R si U=5V et I=0.5A",
        "Puissance électrique": "Trouve P avec U=12V et R=3Ω",
        "Résistance équivalente": "Résistances en série 10Ω, 20Ω",
        "Question IA simple": "Qui es-tu ?",
        "Question IA complexe": "Qui a écrit 'Les Misérables' ?",
        "Réponse vide": "asdgfghjkl"
    }

    for nom, msg in tests.items():
        res = tester_requete(msg)
        if res.startswith("❌") or res.startswith("⏰"):
            print(f"[ERREUR] {nom} → {res}")
        elif "réformuler" in res or "préciser" in res:
            print(f"[ALERTE] {nom} → {res}")
        else:
            print(f"[OK] {nom} → {res}")

    print("\n✅ Fin des tests")


if __name__ == "__main__":
    run_tests()