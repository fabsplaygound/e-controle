__docformat__ = "reStructuredText"
from dotenv import load_dotenv
import logging
import os
import sys
from wsgidav.fs_dav_provider import FilesystemProvider
from wsgidav._version import __version__
from wsgidav.wsgidav_app import DEFAULT_CONFIG, WsgiDAVApp


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecc.settings")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=env_path, override=True)
from ecc import settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ecc.settings'
import django
django.setup()
from webdav.cc_domain_controller import CCDomainController
rootpath = settings.MEDIA_ROOT

provider = FilesystemProvider(rootpath, readonly=True)

logging.basicConfig(level=logging.DEBUG)

config = DEFAULT_CONFIG.copy()
config.update({
  "provider_mapping": {"/": provider},
  "http_authenticator": {
    "domain_controller": CCDomainController,
    "accept_basic": True, "accept_digest": False,
    "default_to_digest": False,
  },
  "verbose": 4,
  "enable_loggers": [],
  "property_manager": True,  # True: use property_manager.PropertyManager
  "lock_manager": True,  # True: use lock_manager.LockManager
})
app = WsgiDAVApp(config)

def application(environ, start_response):
  return app(environ, start_response)
