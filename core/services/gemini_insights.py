import os
import json
import logging
from google import genai
from google.genai import types
from movies.models import Movie, AIInsight
from system.models import SystemLog

logger = logging.getLogger(__name__)

def generate_movie_insights():
    """
    Gera insights estratégicos sobre a indústria cinematográfica usando o Gemini 3.0 Flash.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        msg = "GEMINI_API_KEY não configurada nas variáveis de ambiente."
        logger.error(msg)
        SystemLog.objects.create(level="ERROR", message=msg, source="gemini_service")
        return

    client = genai.Client(api_key=api_key)

    SystemLog.objects.create(level="INFO", message="Iniciando processo de geração de insights com Gemini...", source="gemini_service")

    # 1. Preparar Insumos: 20 filmes mais populares
    movies = Movie.objects.all().order_by('ranking')[:20]
    if not movies.exists():
        msg = "Abortando geração de insights: Nenhum filme encontrado no banco."
        logger.warning(msg)
        SystemLog.objects.create(level="WARNING", message=msg, source="gemini_service")
        return

    SystemLog.objects.create(level="INFO", message=f"Insumos coletados: {movies.count()} filmes e {len(AIInsight.objects.all()[:10])} artigos anteriores.", source="gemini_service")

    movies_data = []
    # ... (loop dos filmes)
    for m in movies:
        movies_data.append({
            "ranking": m.ranking,
            "titulo": m.titulo,
            "sinopse": m.sinopse,
            "faturamento_bruto_mundial": m.faturamento_bruto_mundial,
            "generos": m.generos,
            "data_lancamento": str(m.data_lancamento) if m.data_lancamento else "",
            "duracao_minutos": m.duracao_minutos,
            "proporcao": m.proporcao,
            "url": m.url,
            "created_at": str(m.created_at),
            "updated_at": str(m.updated_at)
        })

    # 2. Preparar Insumos: Últimos 10 artigos
    last_articles = AIInsight.objects.all().order_by('-created_at')[:10]
    last_titles = [article.titulo for article in last_articles]

    # 3. Construir o Prompt
    # ... (prompt)
    input_text = f"""
Você atuará como redator especializado em indústria cinematográfica, criando artigos para um blog voltado a produtores de filmes e cinéfilos avançados. Sua missão é oferecer insights estratégicos sobre tendências da indústria, com base em dados recentes.

Insumos que receberá:
1. Uma lista contendo os 20 filmes mais populares:
{json.dumps(movies_data, ensure_ascii=False, indent=2)}

2. Uma lista com os títulos dos últimos 10 artigos publicados:
{json.dumps(last_titles, ensure_ascii=False, indent=2) if last_titles else "Lista vazia (cold start)."}

Objetivo do artigo:
Com base nos 20 filmes, você deverá:
- Identificar padrões, tendências, correlações ou sinais relevantes para produtores e analistas da indústria.
- Criar um novo artigo cujo tema seja diferente de todos os últimos 10 artigos, evitando repetição conceitual ou estrutural.
- Desenvolver um conteúdo profundo, baseado em dados, com interpretação crítica e insights inéditos.

Restrições obrigatórias:
- O resultado deve ser exclusivamente um JSON contendo os campos: titulo, introducao, desenvolvimento, conclusao.
- Não adicione comentários, explicações extras, markdown ou qualquer outro texto além do JSON final.
- O estilo deve ser analítico, profissional, orientado a tendências e estratégias.
"""

    model_id = "gemini-1.5-flash"
    SystemLog.objects.create(level="INFO", message=f"Usando modelo: {model_id}", source="gemini_service")
    
    try:
        SystemLog.objects.create(level="INFO", message=f"Enviando solicitação para o modelo {model_id}...", source="gemini_service")
        
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="application/json",
        )

        response = client.models.generate_content(
            model=model_id,
            contents=[input_text],
            config=generate_content_config,
        )

        # Processar resposta
        result_json = json.loads(response.text)
        
        # 4. Salvar no Banco de Dados
        new_insight = AIInsight.objects.create(
            titulo=result_json.get("titulo"),
            introducao=result_json.get("introducao"),
            desenvolvimento=result_json.get("desenvolvimento"),
            conclusao=result_json.get("conclusao"),
        )
        
        SystemLog.objects.create(level="INFO", message=f"Insight gerado com sucesso: ID {new_insight.id} - '{new_insight.titulo}'", source="gemini_service")

    except Exception as e:
        error_msg = f"Falha crítica na geração de insights: {str(e)}"
        logger.error(error_msg)
        SystemLog.objects.create(level="ERROR", message=error_msg, source="gemini_service")

if __name__ == "__main__":
    generate_movie_insights()
