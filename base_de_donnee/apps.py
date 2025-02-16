from django.apps import AppConfig


class BaseDeDonneeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base_de_donnee'

class YourAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "base_de_donnee"

    def ready(self):
        import base_de_donnee.signals  # Import the signals