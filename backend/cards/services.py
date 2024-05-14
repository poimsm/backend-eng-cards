# services.py

import json
import logging

from cards.models import (
    ClusterCard,
    CustomCard,
    BasicCard,
    Sticker,
)

from common.models import Status as StatusModel

logger = logging.getLogger('api_v1')


# def create_card(title, description, user):
#     card = Card(title=title, description=description, created_by=user)
#     card.save()
#     return card

# def update_card(card_id, **kwargs):
#     card = Card.objects.filter(id=card_id).update(**kwargs)
#     return card

# def delete_card(card_id):
#     card = Card.objects.get(id=card_id)
#     card.delete()


def get_translation(obj_list, lang_code):
    english_text = None
    for item in obj_list:
        if item['code'] == 'en':
            english_text = item['text']
            break

    translation = None
    for item in obj_list:
        if item['code'] == lang_code:
            translation = item['text']

    return {
        'text': english_text,
        'translation': translation
    }


def get_english_text(obj_list):
    english_text = None
    for item in obj_list:
        if item['code'] == 'en':
            english_text = item['text']
            break

    return english_text


def get_cluster_card(card_id, lang_code):
    card = ClusterCard.objects.get(
        id=card_id,
        status=StatusModel.ACTIVE,
    )

    return {
        'id': card.id,
        'image_url': card.image_url,
        'cluster': card.cluster,
    }


def get_basic_card(card_id, lang_code):
    card = BasicCard.objects.get(
        id=card_id,
        status=StatusModel.ACTIVE,
    )

    examples = []
    for example in card.examples or []:
        example_transl = get_translation(example['example'], lang_code)
        examples.append({
            'example': example_transl,
            'image_url': example['image_url']
        })

    scenarios = []
    for scenario in card.scenarios or []:
        title = get_translation(scenario['title'], lang_code)

        answers = []
        for answer in scenario['answers']:
            answer_transl = get_translation(answer, lang_code)
            answers.append(answer_transl)

        scenarios.append({
            'title': title,
            'image_url': scenario['image_url'],
            'answers': answers
        })

    exaplantion_items = []
    for expl_item in card.explanations or []:
        expl_transl = get_translation(expl_item, lang_code)
        exaplantion_items.append(expl_transl)

    vocab_items = []
    for vocab in card.vocabs or []:
        vocab_items.append({
            'phrase': get_translation(vocab['phrase'], lang_code),
            'matches': vocab['matches'],
            'meaning': vocab['meaning'],
            'examples': vocab['examples'],
        })

    compare_items = []
    for compare in card.compare or []:
        compare_items.append({
            'text': get_translation(compare['text'], lang_code),
            'bold': compare['bold'],
        })

    return {
        'id': card.id,
        'phrase': get_translation(card.phrase, lang_code),
        'image_url': card.image_url,
        'cover_url': card.cover_url,
        'voice': card.voice,
        'meaning': get_translation(card.meaning, lang_code),
        'examples': examples,
        'scenarios': scenarios,
        'vocabs': vocab_items,
        'compare': compare_items,
        'explanations': exaplantion_items,
    }


def get_custom_card(card_id):
    card = CustomCard.objects.get(
        id=card_id,
        status=StatusModel.ACTIVE,
    )

    sticker = Sticker.objects.get(code=card.sticker_code)

    return {
        'id': card.id,
        'phrase': card.phrase,
        'sticker_code': card.sticker_code,
        'image_url': sticker.image_url,
        'cover_url': sticker.cover_url,
        'meaning': card.meaning,
    }


def get_sticker_by_code(code):
    try:
        return Sticker.objects.get(code=code)
    except Sticker.DoesNotExist:
        return None
