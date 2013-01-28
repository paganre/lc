import os
import sys

path = '/home/ubuntu/lc'
if path not in sys.path:
    sys.path.insert(0, '/home/ubuntu/lc')

os.environ['DJANGO_SETTINGS_MODULE'] = 'lc.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()