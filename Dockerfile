# Usar imagem leve
FROM python:3.12-slim

# Criar diretório de trabalho
WORKDIR /app

# Evitar prompts interativos
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o projeto
COPY . .

# Tornar o entrypoint executável
RUN chmod +x /app/entrypoint.sh

# Expor porta padrão do Django/Gunicorn
EXPOSE 8000

# Usar script de entrada
ENTRYPOINT ["/app/entrypoint.sh"]

# Comando padrão (API)
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]