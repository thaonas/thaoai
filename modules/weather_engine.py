import re
import requests
from datetime import datetime

# Mapping des codes météo vers description
CONDITIONS_METEO = {
    0: "Ensoleillé ☀️",
    1: "Partiellement nuageux ⛅",
    2: "Nuageux ☁️",
    3: "Très nuageux 🌤️",
    45: "Brouillard 🌫️",
    48: "Brouillard givrant 🌫️❄️",
    51: "Pluie légère 🌦️",
    53: "Pluie modérée 🌧️",
    55: "Pluie forte 🌧️🌧️",
    61: "Averses légères 🌦️💧",
    63: "Averses modérées 🌧️💧",
    65: "Averses fortes 🌧️💧🌧️",
    71: "Neige légère ❄️",
    73: "Neige modérée ❄️🌨️",
    75: "Neige forte ❄️❄️🌨️",
    80: "Averses isolées 🌦️",
    81: "Averses fréquentes 🌧️",
    82: "Averses violentes 🌧️🌪️",
    95: "Orage ⚡",
    96: "Orage avec grêle ⚡🧊",
    99: "Orage fort avec grêle ⚡🌧️🧊"
}

# URL Open-Meteo pour la météo actuelle
CURRENT_WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast?"
    "latitude={latitude}&"
    "longitude={longitude}&"
    "current_weather=true&"
    "temperature_unit=celsius&"
    "wind_speed_unit=kmh"
)

# URL Nominatim pour trouver les coordonnées
GEOCODE_URL = (
    " https://nominatim.openstreetmap.org/search?"
    "q={ville}&"
    "format=json&"
    "limit=1"
)

def chercher_coordonnees(ville):
    """Utilise OpenStreetMap/Nominatim pour obtenir les coordonnées"""
    headers = {"User-Agent": "assistant_local_v1.0"}
    url = GEOCODE_URL.format(ville=ville)
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        if 
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print(f"❌ Erreur lors de la recherche des coordonnées : {e}")
    return None, None


def obtenir_meteo_actuelle(ville):
    """Obtient la météo actuelle via Open-Meteo"""
    latitude, longitude = chercher_coordonnees(ville)
    if not latitude or not longitude:
        return None

    try:
        url = CURRENT_WEATHER_URL.format(latitude=latitude, longitude=longitude)
        response = requests.get(url)
        data = response.json()

        current = data.get("current_weather", {})
        temperature = current.get("temperature")
        windspeed = current.get("windspeed")
        weathercode = current.get("weathercode")

        condition_text = CONDITIONS_METEO.get(weathercode, f"Code inconnu {weathercode}")

        return {
            "ville": ville,
            "temp": temperature,
            "vent": windspeed,
            "condition": condition_text
        }
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de la météo : {e}")
        return None


def traiter_meteo(message):
    message = message.lower().strip()

    # Recherche une ville ou un lieu dans le message
    pattern = r"(?:météo|temps|pluie|neige)\s+(?:à|de|pour|dans)?\s+([a-zàâäéèêëïîôöùûüç\s]+)"
    match = re.search(pattern, message, re.IGNORECASE)
    if not match:
        return None

    ville = match.group(1).strip()
    if not ville:
        return None

    data = obtenir_meteo_actuelle(ville)
    if not 
        return None

    return (
        f"Météo actuelle à {data['ville'].capitalize()} : \n"
        f"🌡️ Température : {data['temp']}°C\n"
        f"{data['condition']}\n"
        f"🌬️ Vitesse du vent : {data['vent']} km/h"
    )