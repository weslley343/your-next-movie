from django.core.management.base import BaseCommand
from core.services.scrape_movies import should_run_scraper, run_imdb_scraper

class Command(BaseCommand):
    help = "Executa o scraper do IMDB se o banco estiver vazio ou se os dados tiverem mais de 2 horas."

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a execução do scraper independente do tempo.',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        if should_run_scraper(force=force):
            self.stdout.write(self.style.SUCCESS("Iniciando scraper..."))
            run_imdb_scraper()
            self.stdout.write(self.style.SUCCESS("Scraper finalizado."))
        else:
            self.stdout.write(self.style.WARNING("Scraper não é necessário no momento."))
