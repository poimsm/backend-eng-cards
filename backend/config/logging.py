import os

loggers_config = {
    'django': {
        'filename': 'django.log',
        'formatter': 'verbose',
        'level': 'DEBUG'
    },
    'api_v1': {
        'filename': 'api_v1.log',
        'formatter': 'normal',
        'level': 'INFO'
    },
    'text_analyzer': {
        'filename': 'text_analyzer.log',
        'formatter': 'normal',
        'level': 'INFO'
    },
    'audio_converter': {
        'filename': 'audio_converter.log',
        'formatter': 'normal',
        'level': 'INFO'
    },
}


def logger_builder(loggers_config):
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'normal': {
                'format': '%(levelname)s %(asctime)s %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
        },
        'loggers': {}
    }

    base_dir = os.path.dirname(os.path.dirname(__file__))
    log_directory = os.path.join(base_dir, 'logs')

    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    for logger, config in loggers_config.items():
        log_file_path = os.path.join(log_directory, config['filename'])

        # Crear el archivo si no existe
        if not os.path.exists(log_file_path):
            open(log_file_path, 'a').close()

        handler_name = f'file_{logger}'
        LOGGING['handlers'][handler_name] = {
            'level': config['level'],
            'class': 'logging.FileHandler',
            'filename': log_file_path,
            'formatter': config['formatter']
        }
        LOGGING['loggers'][logger] = {
            'handlers': [handler_name],
            'level': config['level'],
            'propagate': True
        }

    return LOGGING


LOGGING = logger_builder(loggers_config)
