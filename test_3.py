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
    # GÊNEROS
    # ============================
    generos = []
    genre_list = soup.find("li", {"data-testid": "storyline-genres"})
    if genre_list:
        generos = [a.get_text(strip=True) for a in genre_list.find_all("a")]

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
        ", ".join(generos),
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

    # Para testes rápidos, vamos limitar a 3 filmes
    # filmes = filmes[:3]
    
    random.shuffle(filmes)
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
            wait_time = random.randint(3, 6) # Reduzi o tempo para o teste ser mais rápido
            logging.info(f"Aguardando {wait_time}s...")
            time.sleep(wait_time)

            try:
                (
                    sinopse,
                    faturamento,
                    generos,
                    data_lancamento,
                    duracao_minutos,
                    proporcao
                ) = scrape_movie_details(driver, movie["link"])

                writer.writerow([
                    movie["ranking"],
                    movie["titulo"],
                    sinopse,
                    faturamento,
                    generos,
                    data_lancamento,
                    duracao_minutos,
                    proporcao,
                    movie["link"]
                ])

                logging.info(f"OK: {movie['titulo']}")

            except Exception as e:
                logging.error(f"Erro ao processar {movie['titulo']}: {e}")

    driver.quit()
    logging.info("Coleta finalizada!")


if __name__ == "__main__":
    main()