from django.contrib import admin

import apps.models.models as app_models

for model in app_models.__dict__.values():
    if isinstance(model, type) and issubclass(model, app_models.models.Model):
        admin.site.register(model)
