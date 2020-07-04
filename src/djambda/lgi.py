import os

from lgi import get_lgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djambda.settings")

application = get_lgi_application()
