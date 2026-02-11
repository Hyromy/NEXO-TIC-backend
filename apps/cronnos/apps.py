from django.apps import AppConfig


class CronJobsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cronnos'

    def ready(self):
        import os
        from . import updater

        if os.getenv("RUN_MAIN"):
            updater.start()
