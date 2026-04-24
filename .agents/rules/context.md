---
trigger: always_on
---

Desafio Técnico - Backend em Django e
PostgreSQL (com Web Scraping)
Estrutura do Desafio:
●​
●​
●​
●​
●​
Web Scraping (em vez de consumo de API)
Armazenamento dos dados
Exposição dos dados através de uma API
Cronjobs
Deploy dos serviços em containers
Ferramentas / Linguagens a serem utilizadas:
●​
●​
●​
●​
●​
●​
●​
Docker
PostgreSQL
Python
Django
Django REST Framework
Celery
Selenium ou Requests + BeautifulSoup
Contexto:
É esperado que obtenhas informações sobre os filmes mais populares do momento
diretamente do site do IMDB e armazená-las numa base de dados.
Parte deste desafio inclui criar e estruturar uma tabela para armazenar informações de
filmes no PostgreSQL.
O scraping deve ser feito a partir da página:
●​ https://www.imdb.com/chart/moviemeter/
Nota:
●​ Não é permitido utilizar APIs oficiais ou wrappers do IMDB.
●​ O scraping deve ser feito utilizando ferramentas como:
○​ requests + BeautifulSoup
○​ SeleniumPassos para completar com sucesso o desafio:
1. Configuração:
a. Ambiente:​
Configura o teu ambiente de desenvolvimento com:
●​ Django
●​ Django REST Framework
●​ Celery
b. Web Scraping:​
Escolhe uma das abordagens:
●​ requests + BeautifulSoup
●​ Selenium
c. Serviços externos:​
Configura um broker para o Celery:
●​ RabbitMQ ou Redis
d. Variáveis de Ambiente:​
Utiliza variáveis de ambiente para:
●​ Configurações do banco
●​ Credenciais
●​ URLs de scraping
2. Criação e Modelagem da Base de Dados:
Cria a tabela Filmes no Django e aplica migrações no PostgreSQL.
Define os campos necessários para armazenar informações relevantes.
Campos obrigatórios:
●​ id
●​ titulo
●​ data_lancamento
●​ ...
3. Web Scraping e Armazenamento:
Cria uma tarefa no Celery que deve executar a cada 2 horas:●​
●​
●​
●​
Acessar a página escolhida do IMDB
Extrair dados dos filmes mais populares
Normalizar os dados
Inserir/atualizar na base de dados
Requisitos:
●​ Evitar duplicações
●​ Tratar falhas de scraping
●​ Implementar logs básicos
4. API Django:
Desenvolva uma API (sem autenticação) usando Django REST Framework que permita:
a. Listar os 20 filmes mais populares, ordenados por popularidade
b. Obter detalhes de um filme específico por ID
c. Criar um novo filme manualmente
d. Atualizar um filme existente
6. Docker:
Orquestra os serviços com Docker:
●​
●​
●​
●​
API (Django)
Banco de dados (PostgreSQL)
Worker (Celery)
Broker (Redis ou RabbitMQ)
Requisitos:
●​ Comunicação entre containers
●​ Uso de docker-compose
●​ Exposição correta de portas
7. Versionamento e Entrega:
O código deve ser disponibilizado em um repositório público no GitHub.
Requisitos do repositório:●​ README com instruções claras para execução do projeto
●​ Passos para subir os containers
●​ Exemplos de uso da API
Observações importantes:
●​ Código limpo e organizado será avaliado
●​ Documentação básica do projeto (README) é essencial
●​ Prazo: 26/04/2026 às 23:59h