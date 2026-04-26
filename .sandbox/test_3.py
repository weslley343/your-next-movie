import csv
import logging
import random
import time
import os
from pathlib import Path
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Load .env
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

INPUT_CSV = "filmes.csv"
OUTPUT_CSV = "detalhes_filmes.csv"


# ============================
#  HELPER: PARSE DURATION
# ============================

def parse_duration(duration_str):
    if not duration_str:
        return None
    try:
        minutes = 0
        parts = duration_str.lower().split()
        for part in parts:
            if 'h' in part:
                minutes += int(part.replace('h', '')) * 60
            elif 'm' in part:
                minutes += int(part.replace('m', ''))
        return minutes
    except:
        return None


# ============================
#  DRIVER
# ============================

def create_driver():
    options = Options()

    # Configurações para rodar em containers
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")

    # User agent para evitar bloqueios
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    selenium_url = os.getenv("SELENIUM_URL")

    if selenium_url:
        logging.info(f"Conectando ao Selenium Remoto: {selenium_url}")
        driver = webdriver.Remote(
            command_executor=selenium_url,
            options=options
        )
    else:
        logging.info("Iniciando Selenium Local...")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

    # Remove navigator.webdriver
    try:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                """
            }
        )
    except Exception:
        pass

    return driver


# ============================
#  SCRAPE DETALHE DO FILME
# ============================

def scrape_movie_details(driver, url):
    logging.info(f"Acessando detalhes: {url}")

    driver.get(url)
    
    # Scroll suave para carregar seções dinâmicas (Gêneros/Tech Specs)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
    time.sleep(1.5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "lxml")

    # ============================
    # SINOPSE
    # ============================
    sinopse_tag = soup.find("div", class_="ipc-html-content-inner-div")
    sinopse = sinopse_tag.get_text(strip=True) if sinopse_tag else None

    # ============================
    # FATURAMENTO BRUTO
    # ============================
    faturamento = None
    boxoffice = soup.find("li", {"data-testid": "title-boxoffice-cumulativeworldwidegross"})
    if boxoffice:
        span = boxoffice.find("span", class_="ipc-metadata-list-item__list-content-item")
        if span:
            faturamento = span.get_text(strip=True)

    # ============================
    # GÊNEROS (Estratégia Ultra-Robusta)
    # ============================
    generos_list = []
    
    # 1. Tenta pelo data-testid padrão
    genre_section = soup.find("li", {"data-testid": "storyline-genres"})
    if not genre_section:
        genre_section = soup.find("div", {"data-testid": "genres"})
    
    # 2. Fallback: Procurar pelo texto "Gêneros" ou "Genres"
    if not genre_section:
        label = soup.find(lambda tag: tag.name in ["span", "li"] and tag.text in ["Gêneros", "Genres"])
        if label:
            genre_section = label.find_parent("li") or label.find_parent("div")

    if genre_section:
        # Pega todos os links dentro da seção encontrada
        links = genre_section.find_all("a")
        # Filtra links que tenham cara de gênero (contendo 'genres=' no link ou classes específicas)
        generos_list = [a.get_text(strip=True) for a in links if a.get_text(strip=True) and ("genres=" in a.get('href', '') or "ipc-metadata-list-item" in str(a.get('class', '')))]

    # 3. Fallback Final: Pegar QUALQUER link que contenha genres= no href na página toda
    if not generos_list:
        all_genre_links = soup.find_all("a", href=lambda x: x and "genres=" in x)
        generos_list = list(set([a.get_text(strip=True) for a in all_genre_links if a.get_text(strip=True)]))

    if not generos_list:
        logging.warning("Nenhum gênero capturado para este filme.")
    else:
        logging.info(f"Gêneros encontrados: {', '.join(generos_list)}")

    # ============================
    # DATA DE LANÇAMENTO
    # ============================
    data_lancamento = None
    release_block = soup.find("li", {"data-testid": "title-details-releasedate"})
    if release_block:
        content = release_block.find("div", class_="ipc-metadata-list-item__content-container")
        if content:
            data_lancamento = content.get_text(strip=True)

    # ============================
    # TEMPO DE DURAÇÃO
    # ============================
    duracao_str = None
    duration_block = soup.find("li", {"data-testid": "title-techspec_runtime"})
    if duration_block:
        span = duration_block.find("span", class_="ipc-metadata-list-item__list-content-item")
        if span:
            duracao_str = span.get_text(strip=True)
    
    duracao_minutos = parse_duration(duracao_str)

    # ============================
    # PROPORÇÃO (ASPECT RATIO)
    # ============================
    proporcao = None
    aspect_block = soup.find("li", {"data-testid": "title-techspec_aspectratio"})
    if aspect_block:
        span = aspect_block.find("span", class_="ipc-metadata-list-item__list-content-item")
        if span:
            proporcao = span.get_text(strip=True)

    return (
        sinopse,
        faturamento,
        ", ".join(generos_list),
        data_lancamento,
        duracao_minutos,
        proporcao
    )


# ============================
#  MAIN
# ============================

def main():
    filmes = []
    if not os.path.exists(INPUT_CSV):
        logging.error(f"Arquivo de entrada {INPUT_CSV} não encontrado! Rode o test_2 primeiro.")
        return

    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            filmes.append(row)

    # Para testes rápidos, vamos limitar a 4 filmes
    filmes = filmes[:4]
    
    driver = create_driver()

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "ranking",
            "titulo",
            "sinopse",
            "faturamento_bruto_mundial",
            "generos",
            "data_lancamento",
            "duracao_minutos",
            "proporcao",
            "url"
        ])

        for movie in filmes:
            wait_time = random.randint(2, 4)
            logging.info(f"Aguardando {wait_time}s...")
            time.sleep(wait_time)

            try:
                res = scrape_movie_details(driver, movie["link"])
                
                # Se não veio gênero, salva o HTML para debug
                if not res[2]:
                    with open(f"debug_{movie['ranking']}.html", "w") as df:
                        df.write(driver.page_source)
                    logging.warning(f"HTML de debug salvo em debug_{movie['ranking']}.html")

                writer.writerow([
                    movie["ranking"],
                    movie["titulo"],
                    res[0], # sinopse
                    res[1], # faturamento
                    res[2], # generos
                    res[3], # data
                    res[4], # duracao
                    res[5], # proporcao
                    movie["link"]
                ])

                logging.info(f"OK: {movie['titulo']}")

            except Exception as e:
                logging.error(f"Erro ao processar {movie['titulo']}: {e}")

    driver.quit()
    logging.info("Coleta finalizada!")


if __name__ == "__main__":
    main()