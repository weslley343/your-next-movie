import logging
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

URL = "https://www.imdb.com/chart/moviemeter/"


def create_driver():
    options = Options()

    # 🚫 Não usar headless
    # options.add_argument("--headless=new")

    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # remover sinais de automação
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    # remover "navigator.webdriver"
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


def fetch_html():
    driver = create_driver()

    try:
        logging.info(f"Acessando: {URL}")
        driver.get(URL)

        time.sleep(6)

        html = driver.page_source

        logging.info("HTML capturado com sucesso")
        print(html)

    except Exception as e:
        logging.error(f"Erro: {e}")

    finally:
        driver.quit()


if __name__ == "__main__":
    fetch_html()