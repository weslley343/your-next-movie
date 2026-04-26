import os
import json
import logging
from movies.models import Movie, AIInsight
from system.models import SystemLog

logger = logging.getLogger(__name__)

def generate_movie_insights():
    """
    Gera insights usando Groq (Llama 3) ou OpenAI como fallback.
    """
    # 1. Tentar Groq (Recomendado para testes gratuitos)
    api_key_groq = os.environ.get("GROQ_API_KEY")
    if api_key_groq:
        logger.info("Tentando geração via Groq...")
        return generate_via_groq(api_key_groq)
    
    # 2. Fallback OpenAI
    api_key_openai = os.environ.get("OPENAI_API_KEY")
    if api_key_openai:
        logger.info("Tentando geração via OpenAI...")
        return generate_via_openai(api_key_openai)

    msg = "Nenhuma API Key (GROQ ou OPENAI) configurada."
    logger.error(msg)
    SystemLog.objects.create(level="ERROR", message=msg, source="insight_service")

def generate_via_groq(api_key):
    from groq import Groq
    client = Groq(api_key=api_key)
    
    SystemLog.objects.create(level="INFO", message="Iniciando geração via Groq (Llama 3)...", source="groq_service")
    
    movies_data, last_titles = prepare_data()
    if not movies_data: 
        return

    prompt = build_prompt(movies_data, last_titles)

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um analista de cinema objetivo. Responda apenas em JSON."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=800,  
            stream=False
        )
        content = chat_completion.choices[0].message.content
        
        # Limpar possível markdown do JSON
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        save_insight(content, "groq_service")
    except Exception as e:
        handle_error(e, "groq_service")

def generate_via_openai(api_key):
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    movies_data, last_titles = prepare_data()
    if not movies_data: return

    prompt = build_prompt(movies_data, last_titles)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Usar o modelo 'mini' para economizar tokens e custo
            messages=[
                {"role": "system", "content": "Analista objetivo."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            response_format={"type": "json_object"}
        )
        save_insight(response.choices[0].message.content, "openai_service")
    except Exception as e:
        handle_error(e, "openai_service")

def prepare_data():
    movies = Movie.objects.all().order_by('ranking')[:20]
    if not movies.exists():
        logger.warning("Nenhum filme encontrado para gerar insights.")
        return None, None
    
    movies_data = [{
        "rank": m.ranking,
        "title": m.titulo,
        "sinopse": m.sinopse,
        "gross": f"${m.faturamento_bruto_mundial:,}" if m.faturamento_bruto_mundial else "N/A",
        "genre": m.generos
    } for m in movies]
    
    last_titles = [a.titulo for a in AIInsight.objects.all().order_by('-created_at')[:5]]
    return movies_data, last_titles

def build_prompt(movies_data, last_titles):
    return f"""
Analise estes dados de filmes populares e crie um insight de tendências para produtores:
Dados: {json.dumps(movies_data, ensure_ascii=False)}
Evite repetir insights já feitos. Veja os ultimos títulos insights para não repetir, o título deve ser afirmativo e você não deve mencionar quantidade dos filmes analisados:
Últimos insights: {last_titles}

JSON campos: titulo, introducao (1 parágrafo), desenvolvimento (1 parágrafo), conclusao (1 parágrafo).
"""

def save_insight(content, source):
    # Tentar extrair JSON de blocos markdown se existirem
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
    
    # Tentar encontrar o primeiro '{' e o último '}'
    start = content.find('{')
    end = content.rfind('}')
    if start != -1 and end != -1:
        content = content[start:end+1]

    data = json.loads(content)
    insight = AIInsight.objects.create(
        titulo=data.get("titulo"),
        introducao=data.get("introducao"),
        desenvolvimento=data.get("desenvolvimento"),
        conclusao=data.get("conclusao")
    )
    SystemLog.objects.create(level="INFO", message=f"Insight criado via {source}: {insight.titulo}", source=source)

def handle_error(e, source):
    msg = f"Erro em {source}: {str(e)}"
    logger.error(msg)
    SystemLog.objects.create(level="ERROR", message=msg, source=source)
