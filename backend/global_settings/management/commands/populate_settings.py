from django.core.management.base import BaseCommand
from django.conf import settings as djangoSettings
from django.db import transaction
from global_settings.models import GlobalSetting
from common.helpers import console, read_JSON_file as read_JSON
import traceback


class Command(BaseCommand):
    help = 'Create global settings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la ejecución del comando.',
        )

    def handle(self, *args, **options):
        console.info('--------------------------------')
        console.info('    POPULATE SETTINGS           ')
        console.info('--------------------------------')

        if not djangoSettings.DEBUG and not options['force']:
            self.stdout.write(self.style.ERROR(
                'Proceso abortado. Debes incluir --force para ejecutar este comando.'))
            return

        try:
            self.work_dir = 'data/populate'
            self.populate_settings()
            console.info('Done')

        except Exception as e:
            traceback.print_exc()
            console.error('Process Failed!')

    def populate_settings(self):
        settigns = read_JSON(f'{self.work_dir}/global_settings.json')

        with transaction.atomic():
            for setting in settigns:

                setting_type = setting['type']

                existing_setting = GlobalSetting.objects.filter(
                    type=setting_type)

                if existing_setting.exists():
                    self.delete_setting(setting_type)

                console.info('Populating setting: ' + setting_type)

                if setting_type == 'languages_settings':
                    self.create_lang_setting(setting)
                else:
                    self.create_setting(setting)

    def create_setting(self, data):
        config = GlobalSetting(
            type=data['type'],
            notes=data.get('notes', None),
            extras=data['extras'],
        )
        config.save()

    def create_lang_setting(self, data):
        languages = []
        for lang in data['extras']['languages']:
            languages.append({
                'code': lang['code'],
                'name': lang['name'],
                'image_url': self.create_url(lang['image']),
            })

        config = GlobalSetting(
            type=data['type'],
            notes=data.get('notes', None),
            extras={
                'language_version': data['extras']['language_version'],
                'languages': languages
            }
        )
        config.save()

    def delete_setting(self, setting_type):
        setting = GlobalSetting.objects.get(type=setting_type)
        setting.delete()
        console.info('[x] Deleted existing setting: ' + setting_type)

    # def delete_all_stikers(self):
    #     Sticker.objects.all().delete()

    #     with connection.cursor() as cursor:
    #         cursor.execute(f"ALTER SEQUENCE {Sticker._meta.db_table}_id_seq RESTART WITH 1")
            
    #     console.info('[x] Deleted existing stickers')

    def create_url(self, chunk):
        media = djangoSettings.SITE_DOMAIN + '/media'
        return f"{media}/{chunk}" if chunk else None
