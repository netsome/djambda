import psycopg2
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class Command(BaseCommand):
    help = "Drop database"

    def add_arguments(self, parser):
        parser.add_argument("db_name")

    def handle(self, *args, **options):
        connection = psycopg2.connect(
            user=settings.DATABASES["default"]["USER"],
            password=settings.DATABASES["default"]["PASSWORD"],
            host=settings.DATABASES["default"]["HOST"],
            port=settings.DATABASES["default"]["PORT"],
        )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with connection.cursor() as cursor:
            cursor.execute(f"DROP DATABASE \"{options['db_name']}\"")
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully dropped database "%s"' % options["db_name"]
            )
        )
