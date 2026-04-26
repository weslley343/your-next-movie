import os
import logging
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Carrega variáveis do .env
load_dotenv()

def test_remote_selenium():
    selenium_url = os.getenv("SELENIUM_URL", "http://localhost:4444/wd/hub")
    
    logging.info(f"Tentando conectar ao Selenium em: {selenium_url}")
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        # Inicia o driver remoto
        driver = webdriver.Remote(
            command_executor=selenium_url,
            options=options
        )
        
        logging.info("Conexão estabelecida com sucesso!")
        
        # Acessa uma página simples
        url = "https://example.com"
        logging.info(f"Acessando: {url}")
        driver.get(url)
        
        # Extrai o título
        title = driver.title
        logging.info(f"Título da página: {title}")
        
        # Extrai o conteúdo do H1
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "lxml")
        h1_text = soup.find("h1").get_text()
        logging.info(f"Texto do H1: {h1_text}")
        
        driver.quit()
        logging.info("Teste finalizado com sucesso!")
        
    except Exception as e:
        logging.error(f"Erro durante o teste: {e}")

if __name__ == "__main__":
    test_remote_selenium()
