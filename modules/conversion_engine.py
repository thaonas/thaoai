import re

conversions = {
    # Longueur
    "mm": ("mètre", 0.001),
    "cm": ("mètre", 0.01),
    "dm": ("mètre", 0.1),
    "m": ("mètre", 1),
    "mètre": ("mètre", 1),
    "metre": ("mètre", 1),
    "mètres": ("mètre", 1),
    "metres": ("mètre", 1),
    "dam": ("mètre", 10),
    "hm": ("mètre", 100),
    "km": ("mètre", 1000),
    "mile": ("mètre", 1609.34),
    "miles": ("mètre", 1609.34),
    "pouce": ("mètre", 0.0254),
    "pouces": ("mètre", 0.0254),

    # Masse
    "mg": ("kg", 0.000001),
    "g": ("kg", 0.001),
    "gramme": ("kg", 0.001),
    "grammes": ("kg", 0.001),
    "dag": ("kg", 0.01),
    "hg": ("kg", 0.1),
    "kg": ("kg", 1),
    "kilogramme": ("kg", 1),
    "kilogrammes": ("kg", 1),
    "tonne": ("kg", 1000),
    "tonnes": ("kg", 1000),

    # Température
    "°f": ("°c", lambda x: (x - 32) * 5 / 9),
    "fahrenheit": ("°c", lambda x: (x - 32) * 5 / 9),
    "°c": ("°c", lambda x: x),
    "celsius": ("°c", lambda x: x),
    "kelvin": ("°c", lambda x: x - 273.15),

    # Temps
    "ms": ("seconde", 0.001),
    "milliseconde": ("seconde", 0.001),
    "millisecondes": ("seconde", 0.001),
    "s": ("seconde", 1),
    "seconde": ("seconde", 1),
    "secondes": ("seconde", 1),
    "min": ("seconde", 60),
    "minute": ("seconde", 60),
    "minutes": ("seconde", 60),
    "h": ("seconde", 3600),
    "heure": ("seconde", 3600),
    "heures": ("seconde", 3600),
    "jour": ("seconde", 86400),
    "jours": ("seconde", 86400),

    # Volume
    "ml": ("litre", 0.001),
    "cl": ("litre", 0.01),
    "dl": ("litre", 0.1),
    "l": ("litre", 1),
    "litre": ("litre", 1),
    "litres": ("litre", 1),
    "m3": ("litre", 1000),
    "gallon": ("litre", 3.78541),
    "gallons": ("litre", 3.78541),

    # Préfixes métriques
    "nano": ("", 1e-9),
    "micro": ("", 1e-6),
    "milli": ("", 0.001),
    "centi": ("", 0.01),
    "déci": ("", 0.1),
    "deci": ("", 0.1),
    "déca": ("", 10),
    "deca": ("", 10),
    "hecto": ("", 100),
    "kilo": ("", 1000),
    "méga": ("", 1e6),
    "mega": ("", 1e6),
    "giga": ("", 1e9),
}

def traiter_conversion(message):
    try:
        message = message.lower().strip()
        message = message.replace("converti", "convertir").replace("mettre", "convertir")
        
        pattern = r"(?:convertir|conversion|calcule|donne|trouve|passer|changer|transforme)\s+(\d+(?:\.\d+)?)\s*([a-z°]+)(?:\s+en|\s+to)\s+([a-z°]+)"
        match = re.fullmatch(pattern, message, re.IGNORECASE)

        if not match:
            return None

        valeur_str, unite_source, unite_cible = match.groups()
        valeur = float(valeur_str)

        if unite_source not in conversions or unite_cible not in conversions:
            return None

        unite_ref_source, facteur_source = conversions[unite_source]
        unite_ref_cible, facteur_cible = conversions[unite_cible]

        if not isinstance(facteur_source, (int, float)) or not isinstance(facteur_cible, (int, float)):
            return None

        if unite_ref_source != unite_ref_cible:
            return f"❌ Impossible de convertir {unite_source} en {unite_cible}."

        valeur_en_ref = valeur * facteur_source
        valeur_cible = valeur_en_ref / facteur_cible

        return f"{valeur} {unite_source} = {valeur_cible:.4f} {unite_cible}"

    except Exception as e:
        print(f"[ERREUR] conversion_engine.traiter_conversion : {e}")
        return None