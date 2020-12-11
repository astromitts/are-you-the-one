import os
from project.settings import *  # noqa
import dj_database_url

DATABASES['default'] = dj_database_url.config(conn_max_age=600)
DATABASES['default'] = dj_database_url.config(default=os.environ['DATABASE_URL'])

DEBUG = True

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ALLOWED_HOSTS = ['aytocalc.herokuapp.com', 'herokuapp.com',]


ENVIRONMENT = 'production'
