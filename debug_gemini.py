import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def generate():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY não configurada.")
        return

    client = genai.Client(
        api_key=api_key,
    )

    # Usando o modelo e configurações EXATOS do template do AI Studio
    model = "gemini-3-flash-preview"
    
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Diga 'Olá Mundo' e faça uma breve análise sobre o futuro do cinema."""),
            ],
        ),
    ]
    
    tools = [
        types.Tool(googleSearch=types.GoogleSearch()),
    ]
    
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="MEDIUM",
        ),
        tools=tools,
        system_instruction=[
            types.Part.from_text(text="""Você atuará como redator especializado em indústria cinematográfica..."""),
        ],
    )

    print(f"🚀 Iniciando geração com o modelo {model}...")

    try:
        # Usando stream conforme o template
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if text := chunk.text:
                print(text, end="", flush=True)
        print("\n\n✅ Geração concluída com sucesso!")
        
    except Exception as e:
        print(f"\n\n❌ ERRO NA GERAÇÃO:")
        print(e)

if __name__ == "__main__":
    generate()