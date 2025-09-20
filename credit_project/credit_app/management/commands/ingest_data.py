from django.core.management.base import BaseCommand
from credit_app.tasks import process_data_files

class Command(BaseCommand):
    help = 'Ingest data from Excel files'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data ingestion...'))
        results = process_data_files()
        for result in results:
            self.stdout.write(self.style.SUCCESS(result))
        self.stdout.write(self.style.SUCCESS('Data ingestion completed!'))