# services.py

from global_settings.models import (
    GlobalSetting,
)


def check_language_exist(lang_code):
    data = GlobalSetting.objects.get(type='languages_settings')
    found = False

    for lang in data.extras['languages']:
        if lang['code'] == lang_code:
            found = True
            break

    return found


def get_cards_settings():
    data = GlobalSetting.objects.get(type='cards_settings')
    return data


def get_languages_info():
    data = GlobalSetting.objects.get(type='languages_settings')
    return {
        'language_version': data.extras['language_version'],
        'languages': data.extras['languages'],
    }


def list_languages():
    data = GlobalSetting.objects.get(type='languages_settings')
    languages = data.extras['languages']
    sorted_languages = sorted(languages, key=lambda x: x['name'])
    return sorted_languages


def get_mobile_app_info():
    data = GlobalSetting.objects.get(type='mobile_settings')
    return data.extras
