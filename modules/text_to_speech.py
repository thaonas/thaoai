import pyttsx3

engine = pyttsx3.init()

# Choisir une voix française si disponible
voices = engine.getProperty('voices')
for voice in voices:
    langs = voice.languages
    if langs and langs[0]:
        lang = langs[0]
        if isinstance(lang, bytes):
            lang = lang.decode()
        if "fr" in lang.lower():
            engine.setProperty('voice', voice.id)
            break

engine.setProperty('rate', 150)  # Vitesse de lecture
engine.setProperty('volume', 0.8)  # Volume


def speak(text):
    engine.stop()  # Arrête toute lecture en cours
    engine.say(text)
    engine.runAndWait()