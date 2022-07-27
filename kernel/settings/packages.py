import os
from datetime import timedelta

from decouple import config
from django.conf import settings

from .base import (
    INSTALLED_APPS, MIDDLEWARE,
    STATIC_ROOT, BASE_DIR, STATICFILES_DIRS
)

# ############## #
#   EXTENSIONS   #
# ############## #

# admin
INSTALLED_APPS.append('django.contrib.admindocs')
INSTALLED_APPS.append('django.contrib.sites')

# packages
INSTALLED_APPS.append('admin_footer')
INSTALLED_APPS.append('admin_honeypot')

# Log

# Security

# Applications
INSTALLED_APPS.append('entry')

# ########### #
#   UPLOAD    #
# ########### #
# FILE_UPLOAD_HANDLERS = [
#     'painless.utils.handlers.upload.ChunkFileUploadHandler'
# ]
# UPLOAD_CHUNK_SIZE = 2500 * 2 ** 10  # 2500 KB

# ######################### #
#       AdminInterface      #
# ######################### #
from datetime import datetime

ADMIN_FOOTER_DATA = {
    'site_url': 'https://entry.com',
    'site_name': 'Entry',
    'period': '{}'.format(datetime.now().year),
    'version': 'v0.0.1 - development'
}

# #################### #
# IMPORTANT VARIABLES  #
# #################### #
# AUTH_USER_MODEL = 'accounts.CustomUser'
