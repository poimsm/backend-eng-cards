from django.core.management.base import BaseCommand
from django.db import connection
from common.helpers import console
from django.conf import settings


class Command(BaseCommand):
    help = 'Borra toda la base de datos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la ejecución del comando para borrar la base de datos.',
        )

    def handle(self, *args, **options):
        console.info('--------------------------------')
        console.info('   DELETING DATABASE....        ')
        console.info('--------------------------------')

        if not settings.DEBUG and not options['force']:
            self.stdout.write(self.style.ERROR('Proceso abortado. Debes incluir --force para ejecutar este comando.'))
            return

        tables_to_truncate = [
            'devices_cards',
            'screenflow',
            'devices_categories',
            'devices_profiles',
            'users_history',
            'users_profiles',
            'devices',
            'cards',
            'categories',
            'packages',
            'devices_packages'
        ]

        with connection.cursor() as cursor:
            cursor.execute('SET session_replication_role = replica;')  # Deshabilita la verificación de clave foránea temporalmente
            for table in tables_to_truncate:
                # RESTART IDENTITY resetea los contadores de las columnas serial/autoincremental
                # CASCADE realiza la operación de truncado en cascada a las tablas relacionadas
                cursor.execute(f'TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;')
            cursor.execute('SET session_replication_role = DEFAULT;')  # Habilita la verificación de clave foránea

        self.stdout.write(self.style.SUCCESS('Base de datos borrada correctamente.'))
