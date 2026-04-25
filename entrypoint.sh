#!/bin/bash

# Se qualquer comando falhar, o script para
set -e

# O host do banco costuma ser o nome do serviço no docker-compose
# Se não estiver definido, usamos 'db' como padrão
DB_HOST=${POSTGRES_HOST:-db}
DB_PORT=${POSTGRES_PORT:-5432}

echo "Aguardando o banco de dados ($DB_HOST:$DB_PORT)..."

# Tenta conectar ao banco usando o próprio Django até ter sucesso real
until python manage.py shell -c "import django; from django.db import connection; connection.ensure_connection()" 2>/dev/null; do
  echo "Banco ainda iniciando... aguardando 1 segundo"
  sleep 1
done

echo "Banco de dados pronto!"

# Executa as migrations
echo "Executando migrations..."
python manage.py migrate --noinput

# Coleta arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Cria superusuário se não existir
echo "Criando superusuário..."
python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.getenv('DJANGO_SUPERUSER_USERNAME')
email = os.getenv('DJANGO_SUPERUSER_EMAIL')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
if username and password:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f'Superusuário {username} criado com sucesso.')
    else:
        print(f'Superusuário {username} já existe.')
else:
    print('Variáveis de ambiente para superusuário não configuradas.')
"

# Executa o scraper se solicitado via variável de ambiente
if [ "$RUN_SCRAPER_ON_STARTUP" = "true" ]; then
    echo "Verificando necessidade de rodar o scraper..."
    python manage.py run_scraper_if_needed
fi

# Executa o comando que foi passado para o container (ex: gunicorn ou celery)
echo "Iniciando comando: $@"
exec "$@"
