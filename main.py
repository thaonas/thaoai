# -*- coding: utf-8 -*-
from modules.speech_to_text import listen_and_transcribe
from modules.chatbot import generate_response
from modules.text_to_speech import speak
from modules.memory import save_conversation
import signal
import sys

def assistant_response(user_input):
    reply = generate_response(user_input)
    save_conversation(user_input, reply)
    return reply

def signal_handler(sig, frame):
    speak("Arrêt forcé. À bientôt !")
    print("\nAssistant : Arrêt forcé. À bientôt !")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    print("🎙️ Assistant en écoute. Dis 'stop' pour quitter.")
    while True:
        user_input = listen_and_transcribe()
        if not user_input:
            continue

        print("🗣️ Tu as dit :", user_input)
        if user_input.lower() in ["stop", "quitte", "arrête", "exit"]:
            speak("Très bien, à bientôt !")
            print("🤖 Assistant : Très bien, à bientôt !")
            break

        reply = assistant_response(user_input)
        print("🤖 Assistant :", reply)
        speak(reply)

if __name__ == "__main__":
    main()