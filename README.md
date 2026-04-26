# Your Next Movie 🎬

[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Celery](https://img.shields.io/badge/Celery-5.3-37814A?style=for-the-badge&logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

**Your Next Movie** é uma plataforma inteligente e totalmente automatizada que monitora tendências do IMDb, identifica os filmes mais populares do momento e transforma esses dados em insights estratégicos movidos por IA.

---

## 🚀 Proposta
O projeto utiliza **Web Scraping** de alta precisão para coletar dados em tempo real e processá-los através de modelos de linguagem (IA) para gerar recomendações e análises de mercado para produtores e entusiastas de cinema.

## 🛠️ Tecnologias
- **Backend:** Python / Django / Django REST Framework
- **Automação:** Celery / Celery Beat (Agendamento)
- **Scraping:** Selenium / BeautifulSoup4
- **Banco de Dados:** PostgreSQL
- **Cache/Broker:** Redis
- **IA:** Groq (Llama 3) / OpenAI

---

## 🐳 Setup via Docker (Recomendado)

A maneira mais rápida de rodar o projeto é utilizando o Docker Compose.

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/your-next-movie.git
    cd your-next-movie
    ```

2.  **Configure o ambiente:**
    Copie o modelo de ambiente para Docker:
    ```bash
    cp .env.docker .env
    ```
    *(Opcional) Edite as chaves de API no arquivo `.env` recém-criado.*

3.  **Suba os containers:**
    ```bash
    docker compose up --build
    ```

4.  **Acesse o projeto:**
    - Brief Page: [http://localhost:8000/](http://localhost:8000/)
    - Documentação Swagger: [http://localhost:8000/api/docs/swagger/](http://localhost:8000/api/docs/swagger/)

---

## 💻 Setup Local (Manual)

Se desejar rodar o projeto fora do Docker para desenvolvimento rápido:

1.  **Requisitos:**
    - Python 3.12+
    - PostgreSQL e Redis rodando localmente (ou via Docker).
    - ChromeDriver (ou container do Selenium rodando).

2.  **Ambiente Virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    pip install -r requirements.txt
    ```

3.  **Configuração:**
    Copie o conteúdo de `.env.local` para um novo arquivo `.env`:
    ```bash
    cp .env.local .env
    ```

4.  **Banco de Dados:**
    ```bash
    python manage.py migrate
    ```

5.  **Rodar Servidor:**
    ```bash
    python manage.py runserver
    ```

---

## ⚙️ Variáveis de Ambiente

O projeto utiliza dois arquivos principais de configuração:
-   `.env.docker`: Configurado para a rede interna do Docker (Hostnames `db`, `redis`, etc).
-   `.env.local`: Configurado para acesso via `localhost`.

**Principais variáveis:**
- `GROQ_API_KEY`: Necessária para geração de insights via Llama 3.
- `OPENAI_API_KEY`: Fallback para geração de insights.
- `SELENIUM_URL`: URL do driver do Selenium.

---

## 📝 Documentação da API

A documentação interativa está disponível nos formatos:
-   **Swagger UI:** `/api/docs/swagger/`
-   **Redoc:** `/api/docs/redoc/`
-   **Schema JSON:** `/api/schema/`

---
Desenvolvido com ❤️ por weslley343
