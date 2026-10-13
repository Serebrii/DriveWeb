from time import sleep

from django.core.management import BaseCommand
from django.db import connection, OperationalError
from psycopg2 import OperationalError as Psycopg2OperationalError


class Command(BaseCommand):
    help = "Wait for the database to be fully initialized."

    def handle(self, *args, **options):
        self.stdout.write("Checking if database is ready...")

        while True:
            try:
                connection.ensure_connection()
                self.stdout.write("Database is available")
                break
            except (OperationalError, Psycopg2OperationalError):
                sleep(1)
                self.stdout.write("Waiting for database...")
