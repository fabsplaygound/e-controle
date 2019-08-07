from django.conf import settings as django_settings

# Look for setting values in the global django settings, otherwise use defaults.
NO_USER_CALL_BACK = getattr(django_settings, 'MAGICAUTH_NO_USER_CALL_BACK', 'magicauth.utils.raise_error')
EMAIL_SUBJECT = getattr(django_settings, 'MAGICAUTH_EMAIL_SUBJECT', 'Connexion e-controle')
EMAIL_HTML_TEMPLATE = getattr(django_settings, 'MAGICAUTH_EMAIL_HTML_TEMPLATE', 'magicauth/email.html')
EMAIL_TEXT_TEMPLATE = getattr(django_settings, 'MAGICAUTH_EMAIL_TEXT_TEMPLATE', 'magicauth/email.txt')
FROM_EMAIL = getattr(django_settings, 'MAGICAUTH_FROM_EMAIL')
LOGIN_TEMPLATE = getattr(django_settings, 'MAGICAUTH_LOGIN_TEMPLATE', 'magicauth/login.html')
TOKEN_DURATION = getattr(django_settings, 'MAGICAUTH_TOKEN_DURATION', 5 * 60)
