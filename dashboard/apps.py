from django.apps import AppConfig
import logging
import sys

logger = logging.getLogger(__name__)

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self):
        # Skip background service during migrations or if Fyers is not available
        if 'makemigrations' in sys.argv or 'migrate' in sys.argv:
            return

        try:
            from .services.fyers_background_service import background_service
            background_service.start()
        except ImportError:
            logger.warning("Fyers background service not available - live market data will be disabled")
