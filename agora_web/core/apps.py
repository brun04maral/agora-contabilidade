from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Agora Contabilidade'

    def ready(self):
        """Importa signals quando a app está pronta"""
        import core.signals  # noqa
