import logging
import time
import csv
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Load .env
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

URL = "https://www.imdb.com/chart/moviemeter/"


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


def fetch_movies():
    driver = create_driver()
    data = []

    try:
        logging.info(f"Acessando: {URL}")
        driver.get(URL)

        logging.info("Aguardando carregamento da lista...")
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "ul.ipc-metadata-list"))
            )
        except Exception as e:
            logging.error(f"Timeout ao carregar a lista. Salvando screenshot de erro...")
            driver.save_screenshot("error_screenshot.png")
            # Salva o HTML para análise também
            with open("error_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            raise e

        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")

        ul = soup.find("ul", class_="ipc-metadata-list")

        if not ul:
            logging.error("UL da lista não encontrada!")
            return []

        items = ul.find_all("li")

        logging.info(f"Foram encontrados {len(items)} filmes.")

        ranking = 1
        for li in items:
            if len(data) == 20:
                break

            title_tag = li.find("h3")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)

            a_tag = li.find("a", href=True)
            link = "https://www.imdb.com" + a_tag["href"] if a_tag else None

            img_tag = li.find("img")
            image = img_tag["src"] if img_tag else None

            movie = {
                "ranking": ranking,
                "titulo": title,
                "imagem": image,
                "link": link
            }

            data.append(movie)
            ranking += 1

        return data

    except Exception as e:
        logging.error(f"ERRO: {e}")
        return []

    finally:
        driver.quit()


# ✅ NOVA FUNÇÃO: salvar CSV
def save_to_csv(movies, filename="filmes.csv"):
    if not movies:
        logging.warning("Nenhum dado para salvar no CSV.")
        return

    keys = movies[0].keys()

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(movies)

    logging.info(f"CSV salvo com sucesso: {filename}")


if __name__ == "__main__":
    filmes = fetch_movies()

    for f in filmes:
        print(f)

    save_to_csv(filmes)