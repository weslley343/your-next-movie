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
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='weslley').exists() or User.objects.create_superuser('weslley', 'weddav97@gmail.com', 'iopioip777777758')"

# Executa o comando que foi passado para o container (ex: gunicorn ou celery)
echo "Iniciando comando: $@"
exec "$@"
