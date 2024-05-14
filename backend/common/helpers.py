import json
import os
import random
import string

from django.conf import settings


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class console(object):
    @staticmethod
    def info(msg):
        print(bcolors.BOLD + '[INFO] ' + msg + bcolors.ENDC)

    @staticmethod
    def debug(msg):
        print(bcolors.OKBLUE + '[DEBUG] ' + msg + bcolors.ENDC)

    @staticmethod
    def warning(msg):
        print(bcolors.WARNING + '[WARNING] ' + msg + bcolors.ENDC)

    @staticmethod
    def error(msg):
        print(bcolors.FAIL + '[ERROR] ' + msg + bcolors.ENDC)


def unique(sequence):
    result = []
    for item in sequence:
        if item not in result:
            result.append(item)
    return result


# def read_JSON_file(path):
#     file = open(os.path.join(settings.BASE_DIR, path))
#     data = file.read()
#     file.close()
#     return json.loads(data)

def read_JSON_file(path):
    file_path = os.path.join(settings.BASE_DIR, path)
    if os.path.exists(file_path):
        with open(file_path) as file:
            data = file.read()
            return json.loads(data)
    else:
        return None


def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


def generate_id(length = 10):
    """
    Genera un ID alfanumérico de una longitud especificada.

    Args:
    length (int): Longitud del ID a generar.

    Returns:
    str: Un string alfanumérico de la longitud especificada.
    """
    # Define los caracteres que pueden ser parte del ID
    characters = string.ascii_letters + string.digits

    # Genera un string aleatorio con los caracteres definidos
    alphanumeric_id = ''.join(random.choice(characters) for _ in range(length))

    return alphanumeric_id