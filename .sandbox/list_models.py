import os
from google import genai

def list_models():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY não configurada.")
        return

    client = genai.Client(api_key=api_key)
    print("=== Modelos Disponíveis ===")
    for model in client.models.list():
        print(f"ID: {model.name} | Suporta GenerateContent: {'generateContent' in model.supported_methods}")

if __name__ == "__main__":
    list_models()
