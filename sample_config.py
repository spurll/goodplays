from os import urandom, path


# Web Server
CSRF_ENABLED = True
SECRET_KEY = urandom(30)
PROPAGATE_EXCEPTIONS = True
REMEMBER_COOKIE_NAME = 'goodplays_token'        # Must be unique server-wide.

# SQLAlchemy
basedir = path.abspath(path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(path.join(basedir, 'app.db'))
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Authentication
AUTH_METHOD = 'LDAP'
AUTH_URI = None
LDAP_URI = 'ldap://YOUR.LDAP.URI'
LDAP_SEARCH_BASE = 'ou=????,dc=????,dc=????'

# Admin
ADMIN_USERS = ['USER.ID.HERE']

# Giant Bomb API
GB_API_KEY = 'YOUR_API_KEY'     # Visit https://www.giantbomb.com/api/

# Steam API
STEAM_API_KEY = 'YOUR_API_KEY'  # Visit https://steamcommunity.com/dev/apikey

# HowLongToBeat
SHOW_HLTB = True
