from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from cards.models import BasicCard, ClusterCard, Category
from common.helpers import console, read_JSON_file as read_JSON
import traceback
from django.db import connection

class Command(BaseCommand):
    help = 'Create cards'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fuerza la ejecución del comando.',
        )

    def handle(self, *args, **options):
        console.info('--------------------------------')
        console.info('    POPULATE CARDS              ')
        console.info('--------------------------------')

        if not settings.DEBUG and not options['force']:
            self.stdout.write(self.style.ERROR(
                'Proceso abortado. Debes incluir --force para ejecutar este comando.'))
            return

        try:
            self.work_dir = 'data/populate'
            self.delete_all_cards()
            self.populate_cards()
            console.info('Done')

        except Exception as e:
            traceback.print_exc()
            console.error('Process Failed!')

    def populate_cards(self):
        with transaction.atomic():
            categories = read_JSON(f'{self.work_dir}/categories.json')

            for category_data in categories:
                self.create_category_and_cards(category_data)

    def create_category_and_cards(self, category_data):
        console.info('Creating category: ' + category_data['name'])
        category = Category(
            name=category_data['name'],
            code=category_data['code'],
            extras=category_data.get('extras', None),
        )
        category.save()

        cards = read_JSON(f'{self.work_dir}/cards.json')
        cards = [card for card in cards if category_data['code']
                 in card['category_codes']]

        card_counter = 0

        for card_data in cards:
            if card_data['type'] == 'basic':
                self.create_basic_card(category, card_data)
            if card_data['type'] == 'cluster':
                self.create_cluster_card(category, card_data)
            card_counter += 1

        console.info(f'Total cards created: {card_counter}')

    def create_basic_card(self, category, card_data):
        IMG_EXTENSION = 'jpg'
        code = card_data['code']
        transl = f'{self.work_dir}/translations/basic'
        content = f'{self.work_dir}/content/basic'
        media = f'cards/basic_cards'

        # --------------- Phrase ---------------------
        phrase = read_JSON(f'{transl}/phrases/{code}.json')

        # --------------- Meaning ---------------------
        meaning = read_JSON(f'{transl}/meanings/{code}.json')

        # --------------- Examples ---------------------
        examples_json = read_JSON(f'{content}/examples/{code}.json')
        examples = []

        if examples_json:
            ex_length = 3 if len(examples_json) > 0 else 0
            ex_length = ex_length if not card_data.get(
                'allowed_examples', None) else card_data['allowed_examples']

            for i in range(ex_length):
                examples.append({
                    'example': read_JSON(f'{transl}/examples/{code}_{i}.json'),
                    'image_url': self.create_url(f'{media}/ex_imgs/{code}_{i}.{IMG_EXTENSION}')
                })

        # --------------- Scenarios ---------------------
        scenarios_json = read_JSON(f'{content}/scenarios/{code}.json')
        scenarios = []

        if scenarios_json:
            for i, sce in enumerate(scenarios_json):
                title_obj = read_JSON(f'{transl}/scenarios/{code}_title.json')

                answers = []
                for j in range(sce['allowed_answers']):
                    ans_transl = read_JSON(
                        f'{transl}/scenarios/{code}_answer_{j}.json')
                    answers.append(ans_transl)

                scenario = sce
                scenario['title'] = title_obj
                scenario['answers'] = answers
                scenario['image_url'] = self.create_url(f'{media}/sce_imgs/{code}_{i}.{IMG_EXTENSION}')
                scenarios.append(scenario)

        # --------------- Explanation ---------------------
        explanations_json = read_JSON(f'{content}/explanations/{code}.json')
        explanations = []

        if explanations_json and explanations_json['explanations']:
            for i in range(len(explanations_json['explanations'])):
                explan_transl = read_JSON(
                    f'{transl}/explanations/{code}_{i}.json')
                explanations.append(explan_transl)

        # ------------------- Voice -------------------------
        voice = None;
        voice_json = read_JSON(f'{content}/voices/{code}.json')
        if voice_json:
            voice = {
                "voice_url": self.create_url(f'{media}/audios/{code}.mp3'),
                "duration": voice_json['duration'],
                "voice_script": voice_json['voice_script']
            }

        # ------------------- Vocab -------------------------
        vocab_list = [];
        vocab_json = read_JSON(f'{content}/vocab/{code}.json')
        if vocab_json:
            for (i, vocab) in enumerate(vocab_json):
                vocab_phrase = read_JSON(f'{transl}/vocab_phrases/{code}_{i}.json')
                vocab_list.append({
                    "phrase": vocab_phrase,
                    "matches": vocab['matches'],
                    "meaning": vocab['meaning'],
                    "examples": vocab['examples'],
                })

        # ------------------- Compare -------------------------
        compare_list = [];
        compare_json = read_JSON(f'{content}/compare/{code}.json')
        if compare_json:
            for (i, compare) in enumerate(compare_json):
                compare_transl = read_JSON(f'{transl}/compare/{code}_{i}.json')
                compare_list.append({
                    "text": compare_transl,
                    "bold": compare['bold'],
                })

        # ------------------ Create Card ----------------------
        card = BasicCard(
            phrase=phrase,
            code=code,
            image_url=self.create_url(f'{media}/imgs/{code}.{IMG_EXTENSION}'),
            cover_url=self.create_url(f'{media}/covers/{code}.{IMG_EXTENSION}'),
            voice=voice,
            meaning=meaning,
            examples=self.return_list_or_none(examples),
            scenarios=self.return_list_or_none(scenarios),
            explanations=self.return_list_or_none(explanations),
            vocabs=self.return_list_or_none(vocab_list),
            compare=self.return_list_or_none(compare_list),
            visible=card_data['visible'],
            status=1
        )
        card.save()

        category.basic_cards.add(card)

    def create_cluster_card(self, category, card_data):

        IMG_EXTENSION = 'jpg'
        card_code = card_data['code']
        content = f'{self.work_dir}/content/clusters'
        cluster = read_JSON(f'{content}/{card_code}.json')
        media = f'cards/cluster_cards'

        card = ClusterCard(
            title=card_data['title'],
            code=card_code,
            image_url=self.create_url(f'{media}/imgs/{card_code}.{IMG_EXTENSION}'),
            cover_url=self.create_url(f'{media}/covers/{card_code}.{IMG_EXTENSION}'),
            cluster=cluster,
            status=1
        )
        card.save()

        category.cluster_cards.add(card)

    def delete_all_cards(self):
        BasicCard.objects.all().delete()
        ClusterCard.objects.all().delete()
        Category.objects.all().delete()

        with connection.cursor() as cursor:
            cursor.execute(f"ALTER SEQUENCE {BasicCard._meta.db_table}_id_seq RESTART WITH 1")
            cursor.execute(f"ALTER SEQUENCE {ClusterCard._meta.db_table}_id_seq RESTART WITH 1")
            cursor.execute(f"ALTER SEQUENCE {Category._meta.db_table}_id_seq RESTART WITH 1")
            
        console.info('[x] Deleted existing cards')

    def create_url(self, chunk):
        media = settings.SITE_DOMAIN + '/media'
        return f"{media}/{chunk}" if chunk else None
    
    def return_list_or_none(self, lst):
        return lst if lst else None
