import logging
import time
import csv

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

URL = "https://www.imdb.com/chart/moviemeter/"


def create_driver():
    options = Options()

    # --- NÃO usar headless ---
    # options.add_argument("--headless=new")

    # Anti-detecção:
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    # Remove navigator.webdriver
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

    return driver


def fetch_movies():
    driver = create_driver()
    data = []

    try:
        logging.info(f"Acessando: {URL}")
        driver.get(URL)

        logging.info("Aguardando carregamento da lista...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "ul.ipc-metadata-list"))
        )

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