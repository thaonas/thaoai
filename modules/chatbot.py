from llama_cpp import Llama
import time

MODELE_PATH = "/home/thao/thaoai/models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf"

print("🔄 Chargement du modèle...")
lm = Llama(
    model_path=MODELE_PATH,
    n_ctx=2048,
    n_threads=6,
    n_batch=128,
    verbose=False
)
print("✅ Modèle chargé.")


def generate_response(message):
    prompt = f"Question : {message.strip()}\nRéponse :"

    try:
        start = time.time()
        output = lm(
            prompt,
            max_tokens=150,
            stop=["\n", "Question"],
            temperature=0.7,
            top_p=0.95,
            echo=False
        )
        end = time.time()
        print(f"⏱️ Temps de génération : {end - start:.2f} secondes")

        texte = output["choices"][0]["text"].strip()
        return texte
    except Exception as e:
        print(f"❌ Erreur lors de la génération : {e}")
        return "Désolé, je n’ai pas pu générer de réponse."