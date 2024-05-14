from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from cards.models import Sticker
from common.helpers import console, read_JSON_file as read_JSON
import traceback
from django.db import connection

class Command(BaseCommand):
    help = 'Create stickers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la ejecución del comando.',
        )

    def handle(self, *args, **options):
        console.info('--------------------------------')
        console.info('    POPULATE STICKERS           ')
        console.info('--------------------------------')

        if not settings.DEBUG and not options['force']:
            self.stdout.write(self.style.ERROR(
                'Proceso abortado. Debes incluir --force para ejecutar este comando.'))
            return

        try:
            self.work_dir = 'data/populate'
            self.delete_all_stikers()
            self.populate_stickers()
            console.info('Done')
        except Exception as e:
            traceback.print_exc()
            console.error('Process Failed!')

    def populate_stickers(self):

        stickers = read_JSON(f'{self.work_dir}/stickers.json')

        with transaction.atomic():
            # Vaciar la tabla de stickers
            Sticker.objects.all().delete()
            console.info('All existing stickers have been deleted.')

            IMG_EXTENSION = 'jpg'

            # Crear y guardar los nuevos stickers
            for sticker in stickers:
                code = sticker['code']
                console.info(f'Creating sticker: {code}')

                new_sticker = Sticker(
                    visible=sticker['visible'],
                    code=code,
                    image_url=self.create_url(f'stickers/{code}L.{IMG_EXTENSION}'),
                    cover_url=self.create_url(f'stickers/{code}.{IMG_EXTENSION}'),
                )
                new_sticker.save()
                # console.info(f'Sticker {code} created successfully.')

    def delete_all_stikers(self):
        Sticker.objects.all().delete()

        with connection.cursor() as cursor:
            cursor.execute(f"ALTER SEQUENCE {Sticker._meta.db_table}_id_seq RESTART WITH 1")
            
        console.info('[x] Deleted existing stickers')

    def create_url(self, chunk):
        media = settings.SITE_DOMAIN + '/media'
        return f"{media}/{chunk}" if chunk else None
        
