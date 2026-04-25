import os
import logging
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from django.utils import timezone
from datetime import timedelta
from movies.models import Movie
from system.models import SystemLog

logger = logging.getLogger(__name__)

# ============================
#  CHECK LOGIC
# ============================

def should_run_scraper(force=False):
    if force:
        return True
        
    # 1. Se não houver filmes, precisa rodar
    if not Movie.objects.exists():
        logger.info("Nenhum filme encontrado no banco. Scraper deve rodar.")
        return True
    
    # 2. Se o último filme atualizado for de mais de 2 horas atrás
    last_update = Movie.objects.order_by('-updated_at').first()
    if last_update:
        # Usar timezone aware datetime
        diff = timezone.now() - last_update.updated_at
        if diff > timedelta(hours=2):
            logger.info(f"Última atualização foi há {diff}. Scraper deve rodar.")
            return True
    
    logger.info("Dados ainda são recentes. Scraper não irá rodar agora.")
    return False

# ============================
#  HELPERS
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

def parse_date(date_str):
    if not date_str:
        return None
    try:
        # Example: "April 17, 2026 (United States)" -> "April 17, 2026"
        clean_date = date_str.split('(')[0].strip()
        return datetime.strptime(clean_date, "%B %d, %Y").date()
    except Exception as e:
        logger.warning(f"Erro ao converter data '{date_str}': {e}")
        return None

def parse_currency(curr_str):
    if not curr_str:
        return None
    try:
        # Example: "$53,571,688" -> 53571688
        return int(curr_str.replace('$', '').replace(',', '').strip())
    except Exception as e:
        logger.warning(f"Erro ao converter faturamento '{curr_str}': {e}")
        return None


# ============================
#  DRIVER SETUP
# ============================

def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    selenium_url = os.getenv("SELENIUM_URL")

    if selenium_url:
        driver = webdriver.Remote(command_executor=selenium_url, options=options)
    else:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
    except:
        pass

    return driver


# ============================
#  SCRAPING LOGIC
# ============================

def fetch_popular_movies_list(driver):
    url = "https://www.imdb.com/chart/moviemeter/"
    driver.get(url)
    
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ul.ipc-metadata-list"))
    )
    
    soup = BeautifulSoup(driver.page_source, "lxml")
    ul = soup.find("ul", class_="ipc-metadata-list")
    if not ul:
        return []

    items = ul.find_all("li")
    movies_data = []
    ranking = 1
    for li in items:
        if len(movies_data) >= 20:
            break
            
        title_tag = li.find("h3")
        if not title_tag:
            continue
        
        title = title_tag.get_text(strip=True)
        a_tag = li.find("a", href=True)
        link = "https://www.imdb.com" + a_tag["href"] if a_tag else None
        
        movies_data.append({
            "ranking": ranking,
            "titulo": title,
            "url": link
        })
        ranking += 1
    
    return movies_data

def scrape_movie_details(driver, url):
    driver.get(url)
    time.sleep(random.uniform(1.5, 3.0))
    soup = BeautifulSoup(driver.page_source, "lxml")

    # Sinopse
    sinopse_tag = soup.find("div", class_="ipc-html-content-inner-div")
    sinopse = sinopse_tag.get_text(strip=True) if sinopse_tag else None

    # Faturamento
    faturamento_str = None
    boxoffice = soup.find("li", {"data-testid": "title-boxoffice-cumulativeworldwidegross"})
    if boxoffice:
        span = boxoffice.find("span", class_="ipc-metadata-list-item__list-content-item")
        if span: faturamento_str = span.get_text(strip=True)

    # Gêneros
    generos = []
    genre_list = soup.find("li", {"data-testid": "storyline-genres"})
    if genre_list:
        generos = [a.get_text(strip=True) for a in genre_list.find_all("a")]

    # Data de Lançamento
    data_str = None
    release_block = soup.find("li", {"data-testid": "title-details-releasedate"})
    if release_block:
        content = release_block.find("div", class_="ipc-metadata-list-item__content-container")
        if content: data_str = content.get_text(strip=True)

    # Duração
    duracao_str = None
    duration_block = soup.find("li", {"data-testid": "title-techspec_runtime"})
    if duration_block:
        span = duration_block.find("span", class_="ipc-metadata-list-item__list-content-item")
        if span: duracao_str = span.get_text(strip=True)

    # Proporção
    proporcao = None
    aspect_block = soup.find("li", {"data-testid": "title-techspec_aspectratio"})
    if aspect_block:
        span = aspect_block.find("span", class_="ipc-metadata-list-item__list-content-item")
        if span: proporcao = span.get_text(strip=True)

    return {
        "sinopse": sinopse,
        "faturamento_bruto_mundial": parse_currency(faturamento_str),
        "generos": ", ".join(generos),
        "data_lancamento": parse_date(data_str),
        "duracao_minutos": parse_duration(duracao_str),
        "proporcao": proporcao
    }


# ============================
#  SERVICE ENTRY POINT
# ============================

def run_imdb_scraper():
    SystemLog.objects.create(level="INFO", message="Iniciando processo de scraping do IMDB...", source="scraper")
    
    driver = None
    try:
        driver = create_driver()
        movies_list = fetch_popular_movies_list(driver)
        
        if not movies_list:
            SystemLog.objects.create(level="ERROR", message="Não foi possível obter a lista de filmes populares.", source="scraper")
            return
        
        total = len(movies_list)
        SystemLog.objects.create(level="INFO", message=f"Lista obtida: {total} filmes encontrados. Iniciando detalhes...", source="scraper")
        
        count = 0
        for i, movie_basic in enumerate(movies_list):
            try:
                logger.info(f"[{i+1}/{total}] Processando: {movie_basic['titulo']}")
                details = scrape_movie_details(driver, movie_basic["url"])
                
                # Update or Create
                Movie.objects.update_or_create(
                    titulo=movie_basic["titulo"],
                    defaults={
                        "ranking": movie_basic["ranking"],
                        "url": movie_basic["url"],
                        "sinopse": details["sinopse"],
                        "faturamento_bruto_mundial": details["faturamento_bruto_mundial"],
                        "generos": details["generos"],
                        "data_lancamento": details["data_lancamento"],
                        "duracao_minutos": details["duracao_minutos"],
                        "proporcao": details["proporcao"],
                    }
                )
                count += 1
                logger.info(f"Filme processado: {movie_basic['titulo']}")
                
            except Exception as e:
                logger.error(f"Erro ao processar filme {movie_basic['titulo']}: {e}")
                continue
        
        SystemLog.objects.create(level="INFO", message=f"Scraping finalizado. {count} filmes atualizados.", source="scraper")
        
    except Exception as e:
        SystemLog.objects.create(level="ERROR", message=f"Falha crítica no scraper: {str(e)}", source="scraper")
        logger.error(f"Critical error in scraper: {e}")
    finally:
        if driver:
            driver.quit()
