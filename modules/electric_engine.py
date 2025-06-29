import re

def loi_dohm(message):
    try:
        message = message.lower().strip()
        match_u = re.search(r"calcule u avec r\s*=\s*(\d+\.?\d*)\s*[ωΩ]?\s*et i\s*=\s*(\d+\.?\d*)\s*a", message)
        match_r = re.search(r"donne r si u\s*=\s*(\d+\.?\d*)\s*v?\s*et i\s*=\s*(\d+\.?\d*)\s*a", message)
        match_i = re.search(r"trouve i avec u\s*=\s*(\d+\.?\d*)\s*v?\s*et r\s*=\s*(\d+\.?\d*)\s*[ωΩ]?", message)

        if match_u:
            r, i = map(float, match_u.groups())
            return f"Tension U = {r} Ω × {i} A = {r * i} V"
        elif match_r:
            u, i = map(float, match_r.groups())
            return f"Résistance R = {u} V ÷ {i} A = {u / i:.2f} Ω"
        elif match_i:
            u, r = map(float, match_i.groups())
            return f"Intensité I = {u} V ÷ {r} Ω = {u / r:.2f} A"
        return None
    except Exception as e:
        print(f"[ERREUR] electric_engine.loi_dohm : {e}")
        return None


def puissance_electrique(message):
    try:
        message = message.lower().strip()
        match_p_ui = re.search(r"calcule p avec u\s*=\s*(\d+\.?\d*)\s*v?\s*et i\s*=\s*(\d+\.?\d*)\s*a", message)
        match_p_ri = re.search(r"donne p avec r\s*=\s*(\d+\.?\d*)\s*[ωΩ]?\s*et i\s*=\s*(\d+\.?\d*)\s*a", message)
        match_p_ur = re.search(r"trouve p avec u\s*=\s*(\d+\.?\d*)\s*v?\s*et r\s*=\s*(\d+\.?\d*)\s*[ωΩ]?", message)

        if match_p_ui:
            u, i = map(float, match_p_ui.groups())
            return f"Puissance P = {u} V × {i} A = {u * i} W"
        elif match_p_ri:
            r, i = map(float, match_p_ri.groups())
            return f"Puissance P = {r} Ω × ({i} A)² = {r * i ** 2} W"
        elif match_p_ur:
            u, r = map(float, match_p_ur.groups())
            return f"Puissance P = ({u} V)² ÷ {r} Ω = {u ** 2 / r:.2f} W"
        return None
    except Exception as e:
        print(f"[ERREUR] electric_engine.puissance_electrique : {e}")
        return None


def resistance_equivalente(message):
    try:
        message = message.lower().strip()
        serie_match = re.search(r"résistances? en série ([\d\.\sΩKkMm]+)", message)
        parallele_match = re.search(r"en parallèle.*?([\d\.\sΩKkMm]+)", message)

        def parse_resistances(text):
            text = text.replace("k", "e3").replace("M", "e6").replace("Ω", "").replace(" ", "")
            return [float(x) for x in re.findall(r"\d+\.?\d*", text)]

        if serie_match:
            resistances = parse_resistances(serie_match.group(1))
            total = sum(resistances)
            return f"Résistance équivalente en série = {total:.2f} Ω"

        if parallele_match:
            resistances = parse_resistances(parallele_match.group(1))
            try:
                total_inv = sum(1 / r for r in resistances if r != 0)
                return f"Résistance équivalente en parallèle = {1 / total_inv:.2f} Ω"
            except ZeroDivisionError:
                return "Impossible de calculer une résistance nulle."

        return None
    except Exception as e:
        print(f"[ERREUR] electric_engine.resistance_equivalente : {e}")
        return None


def traiter_electricite(message):
    try:
        fonctions = [
            loi_dohm,
            puissance_electrique,
            resistance_equivalente
        ]
        for fonction in fonctions:
            resultat = fonction(message)
            if resultat:
                return resultat
        return None
    except Exception as e:
        print(f"[ERREUR] electric_engine.traiter_electricite : {e}")
        return None