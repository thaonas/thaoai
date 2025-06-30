import re
from datetime import datetime, timedelta
import pytz
from pytz import timezone, all_timezones

def trouver_fuseau(message):
    mots = re.findall(r"\b\w+\b", message.lower())
    for mot in mots:
        for zone in all_timezones:
            zone_name = zone.split("/")[-1].lower()
            if mot in zone_name and len(mot) > 3:
                return zone
    return None


def obtenir_heure_actuelle(message):
    try:
        message = message.lower().strip()
        if "heure" in message or "heures" in message or "quelle" in message and ("heure" in message or "h" in message):
            zone_name = trouver_fuseau(message)
            try:
                zone = timezone(zone_name) if zone_name else timezone("UTC")
            except Exception:
                zone = timezone("UTC")

            maintenant = datetime.now(pytz.utc).astimezone(zone)

            format_date = "%A %d %B %Y"
            format_heure = "%H:%M:%S"

            if "date" in message and "heure" in message:
                return f"Aujourd'hui, il est {maintenant.strftime(format_heure)} et nous sommes le {maintenant.strftime(format_date)}."
            elif "heure" in message:
                return f"Il est {maintenant.strftime(format_heure)}."
            elif "date" in message:
                return f"Aujourd'hui, c'est le {maintenant.strftime(format_date)}."
        return None
    except Exception as e:
        print(f"[ERREUR] clock_engine.obtenir_heure_actuelle : {e}")
        return None


def calculer_duree(message):
    try:
        message = message.lower().strip()
        pattern = r"(?:calcule|donne|trouve) ([a-z0-9 ]+)(?:depuis|dans|en) (\d+) ?([a-z]+)"
        match = re.search(pattern, message)

        if not match:
            return None

        _, valeur_str, unite = match.groups()
        valeur = int(valeur_str)

        now = datetime.now()

        if "jour" in unite:
            delta = timedelta(days=valeur)
        elif "heure" in unite:
            delta = timedelta(hours=valeur)
        elif "minute" in unite or "min" in unite:
            delta = timedelta(minutes=valeur)
        elif "seconde" in unite:
            delta = timedelta(seconds=valeur)
        else:
            return None

        result = now + delta if "dans" in message else now - delta
        return f"{valeur} {unite}(s) {'après' if 'dans' in message else 'avant'} : {result.strftime('%Y-%m-%d %H:%M:%S')}"
    except Exception as e:
        print(f"[ERREUR] clock_engine.calculer_duree : {e}")
        return None


def traiter_horloge(message):
    fonctions = [
        obtenir_heure_actuelle,
        calculer_duree
    ]

    for fonction in fonctions:
        try:
            resultat = fonction(message)
            if resultat:
                return resultat
        except Exception as e:
            print(f"[ERREUR] clock_engine.{fonction.__name__} : {e}")
            continue

    return None