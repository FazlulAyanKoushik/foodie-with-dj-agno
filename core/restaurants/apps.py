from django.apps import AppConfig


class RestaurantsConfig(AppConfig):
    name = 'restaurants'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        """
        Import signals when the app is ready.
        """
        import restaurants.signals  # noqa
