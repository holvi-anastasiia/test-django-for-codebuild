# -*- coding: utf-8 -*-
import string
from random import choice
from os import environ

# default the test runner to be nose runner unless set in environment
environ.setdefault('DJANGO_TEST_RUNNER_CLASS',
                   'test_db_in_codebuild.test_runner.DjangoNoseTestSuiteSnapshotDBRunner')

from .base import *

DEBUG = False
TEMPLATE_DEBUG = False

# Opsware tests need admin ui
ENABLE_ADMIN_UI = True

ADMINS = (

)


# Use default as read replica for tests
REPLICA_DB_ALIAS = 'default'

DATABASES = {
    'default': {
        'ENGINE': 'vaultcommon.testutils.test_db_backends.backends.postgresql_psycopg2',
        'NAME': 'test_db',
        'USER': 'test_db_dev',
        'PASSWORD': 'test_db_dev',
        'HOST': '127.0.0.1',
        'PORT': '5432',  
        'ATOMIC_REQUESTS': True,
        'TEST_NAME': "{}_{}".format(
            "".join([choice(string.ascii_letters)
                     for i in xrange(1, 10)]), "test_db_dev"),
        'ATOMIC_REQUESTS': True,
    },
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'CRITICAL',
            'class': 'logging.StreamHandler',
        },
        # a sanitizer of audit
        'auditdb_sanitizer': {
            'level': 'DEBUG',
            'class': 'vault.audit.handlers.AuditHandlerSanitizer',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'oauth2': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        # add the auditdb sanitizer to the ones using it in production
        'vault': {
            'handlers': ['console', 'auditdb_sanitizer'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'vault.bankgwclient': {
            'handlers': ['console', 'auditdb_sanitizer'],
            'level': 'ERROR',
            'propagate': True,
        },
        # reduce weasyprint logging
        'weasyprint': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
