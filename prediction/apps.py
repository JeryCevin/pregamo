from django.apps import AppConfig


class PredictionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prediction'
    
    def ready(self):
        """Import signals saat app ready untuk enable auto-training"""
        # Signals disabled - using synchronous training instead
        # import prediction.signals  # noqa
        pass
