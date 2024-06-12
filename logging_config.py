# *-* coding: utf-8 *-*

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'app.log',  # specify the output log file path
            'maxBytes': 20*1024*1024,  # 20 MB
            'backupCount': 1,  # keep only one backup
            'formatter': 'standard'
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        }
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
