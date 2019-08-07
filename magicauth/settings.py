from django.conf import settings as django_settings

# To add magicauth to your site, you need to add these values to your site settings (the rest have defaults, you are
# free to change them if you want):
# MAGICAUTH_FROM_EMAIL : e.g. 'contact@mysite.com'
# MAGICAUTH_LOGGED_IN_REDIRECT_URL_NAME : e.g. 'home'
#
# Note : for the default templates to be picked up, you need to enable the app_directories template Loader, by setting
# TEMPLATES app_dirs to True.
# https://docs.djangoproject.com/en/2.2/ref/templates/api/#django.template.loaders.app_directories.Loader

# Email settings
EMAIL_SUBJECT = getattr(django_settings, 'MAGICAUTH_EMAIL_SUBJECT', 'Lien de connexion')
EMAIL_HTML_TEMPLATE = getattr(django_settings, 'MAGICAUTH_EMAIL_HTML_TEMPLATE', 'magicauth/email.html')
EMAIL_TEXT_TEMPLATE = getattr(django_settings, 'MAGICAUTH_EMAIL_TEXT_TEMPLATE', 'magicauth/email.txt')
FROM_EMAIL = getattr(django_settings, 'MAGICAUTH_FROM_EMAIL')

# View templates
LOGIN_VIEW_TEMPLATE = getattr(django_settings, 'MAGICAUTH_LOGIN_VIEW_TEMPLATE', 'magicauth/login.html')
EMAIL_SENT_VIEW_TEMPLATE = getattr(django_settings, 'MAGICAUTH_EMAIL_SENT_VIEW_TEMPLATE', 'magicauth/email_sent.html')

# URLs
# Once user has entered email successfully and email has been sent, show this page.
EMAIL_SENT_URL = getattr(django_settings, 'MAGICAUTH_EMAIL_SENT_URL', 'email-envoyé/')
LOGIN_URL = getattr(django_settings, 'MAGICAUTH_LOGIN_URL', 'login/')
LOGOUT_URL = getattr(django_settings, 'MAGICAUTH_LOGOUT_URL', 'logout')
# The emailed links point to this url.
VALIDATE_TOKEN_URL = getattr(django_settings, 'MAGICAUTH_VALIDATE_TOKEN_URL', 'magicauth-validate-token')

# Once user is logged in, redirect to this url (probably your landing page).
LOGGED_IN_REDIRECT_URL_NAME = getattr(django_settings, 'MAGICAUTH_LOGGED_IN_REDIRECT_URL_NAME')

# Other
TOKEN_DURATION = getattr(django_settings, 'MAGICAUTH_TOKEN_DURATION', 5 * 60)
# Function to call when the email entered in the form is not found in the database.
# The default just raises an error whose message gets displayed on the login page.
EMAIL_UNKNOWN_CALLBACK = getattr(django_settings, 'MAGICAUTH_EMAIL_UNKNOWN_CALLBACK', 'magicauth.utils.raise_error')
# If using the default EMAIL_UNKNOWN_CALLBACK, this message will be displayed when an unknown email is entered.
EMAIL_UNKNOWN_MESSAGE = getattr(django_settings, 'MAGICAUTH_EMAIL_UNKNOWN_MESSAGE', 'Aucun utilisateur trouvé.')
