# -*- coding: utf-8 -*-
import os
import time
import numpy as np
import speech_recognition as sr
import whisper
from scipy.io import wavfile

# Options configurables
USE_VAD = True  # Activer la détection de parole (Voice Activity Detection)
WAKE_WORD_MODE = False  # Détecter un mot-clé avant d'écouter ("assistant", "hey")
WHISPER_MODEL = "tiny"  # Peut être "base", "small", etc.
LANGUAGE = "fr"
AUDIO_DIR = "audio"
TIMEOUT_DURATION = 5  # Secondes sans son avant timeout
MIN_AUDIO_LENGTH = 0.5  # Durée minimale d'enregistrement (en secondes)

# Création du dossier audio si nécessaire
os.makedirs(AUDIO_DIR, exist_ok=True)

# Charger le modèle Whisper
print("🔄 Chargement du modèle Whisper...")
model = whisper.load_model(WHISPER_MODEL)
print("✅ Modèle chargé.")

# Charger VAD si disponible
try:
    import webrtcvad
    vad = webrtcvad.Vad()
    vad.set_mode(1)  # Mode sensible (0: moins sensible, 3: très sensible)
except ImportError:
    print("⚠️ webrtcvad non trouvé. Installez-le avec 'pip install webrtcvad'")
    USE_VAD = False


def is_speech(data, sample_rate=16000):
    """Détection basique de parole via webrtcvad."""
    frame_duration = 30  # ms
    frames = [data[i:i + int(sample_rate * frame_duration / 1000)] for i in range(0, len(data), int(sample_rate * frame_duration / 1000))]
    speech_frames = 0
    for frame in frames:
        if len(frame) < int(sample_rate * frame_duration / 1000):
            break
        is_speech = vad.is_speech((frame * 32767).astype(np.int16).tobytes(), sample_rate)
        if is_speech:
            speech_frames += 1
    return speech_frames > 0


def clean_audio_dir():
    """Nettoie les anciens fichiers WAV."""
    for old_file in glob.glob(os.path.join(AUDIO_DIR, "*.wav")):
        try:
            os.remove(old_file)
        except Exception as e:
            print(f"❌ Erreur lors de la suppression : {e}")


def listen_and_transcribe():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300  # Ajustable selon ton micro
    recognizer.dynamic_energy_threshold = True

    try:
        with sr.Microphone() as source:
            print("🎤 Parle maintenant...")

            if WAKE_WORD_MODE:
                print("En attente du mot-clé...")
                while True:
                    audio = recognizer.listen(source, phrase_time_limit=3, timeout=10)
                    try:
                        temp_path = os.path.join(AUDIO_DIR, "temp.wav")
                        with open(temp_path, "wb") as f:
                            f.write(audio.get_wav_data())
                        result = model.transcribe(temp_path, language="fr")
                        text = result["text"].strip().lower()
                        if "assistant" in text or "hey" in text:
                            print("✅ Mot-clé détecté.")
                            break
                    except Exception:
                        continue

            audio = recognizer.listen(source, timeout=TIMEOUT_DURATION)
            audio_data = np.frombuffer(audio.get_raw_data(convert_rate=16000, convert_width=2), dtype=np.int16).astype(np.float32) / 32768.0

            if USE_VAD:
                if not is_speech(audio_data, 16000):
                    print("🔴 Aucune parole détectée.")
                    return ""

            # Sauvegarder l'audio
            clean_audio_dir()
            audio_path = os.path.join(AUDIO_DIR, "input.wav")
            wavfile.write(audio_path, 16000, (audio_data * 32767).astype(np.int16))

            # Transcrire
            print("📝 Transcription en cours...")
            result = model.transcribe(audio_path, language=LANGUAGE)
            return result["text"].strip()

    except sr.WaitTimeoutError:
        print("⏳ Aucun son détecté avant expiration.")
        return ""
    except sr.UnknownValueError:
        print("❓ Audio incompréhensible.")
        return ""
    except Exception as e:
        print(f"❌ Erreur lors de la transcription : {e}")
        return ""