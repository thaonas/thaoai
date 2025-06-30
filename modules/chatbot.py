from llama_cpp import Llama
import time
from threading import Thread, Lock

MODELE_PATH = "/home/thao/thaoai/models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf"

print("🔄 Chargement du modèle...")
lm = Llama(
    model_path=MODELE_PATH,
    n_ctx=2048,
    n_threads=6,
    n_batch=128,
    verbose=False,
    n_gpu_layers=0
)
print("✅ Modèle chargé.")

# Verrou pour éviter les accès parallèles au modèle
model_lock = Lock()

def generate_response(message):
    prompt = f"Question : {message.strip()}\nRéponse :"

    try:
        output = lm(
            prompt,
            max_tokens=60,
            stop=["\n", "Question"],
            temperature=0.7,
            top_p=0.95,
            echo=False
        )
        texte = output["choices"][0]["text"].strip()
        return texte if texte else None
    except Exception as e:
        print(f"❌ Erreur lors de la génération : {e}")
        return None