def charger_contexte(memoire):
    contexte = ""
    for q_or_r, contenu in memoire[:-1]:
        if q_or_r == "Question":
            contexte += f"Question : {contenu}\n"
        else:
            contexte += f"Réponse : {contenu}\n"

    contexte += f"Question : {memoire[-1][1]}\nRéponse :"
    return contexte