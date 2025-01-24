from django.apps import AppConfig


class PdfAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pdf_app'

    def ready(self):
        """
        Import and register signals when the app is ready
        """
        # from . import signals
        # signals.register_pdf_signals()