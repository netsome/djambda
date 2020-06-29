import psycopg2
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class Command(BaseCommand):
    help = "Creates database"

    def add_arguments(self, parser):
        parser.add_argument("db_name")
        parser.add_argument("--exist_ok", action="store_true")

    def handle(self, *args, **options):
        connection = psycopg2.connect(
            user=settings.DATABASES["default"]["USER"],
            password=settings.DATABASES["default"]["PASSWORD"],
            host=settings.DATABASES["default"]["HOST"],
            port=settings.DATABASES["default"]["PORT"],
        )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE \"{options['db_name']}\"")
        except psycopg2.errors.DuplicateDatabase:
            if not options["exist_ok"]:
                raise CommandError('Database "%s" already exists' % options["db_name"])
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully created database "%s"' % options["db_name"]
                )
            )
