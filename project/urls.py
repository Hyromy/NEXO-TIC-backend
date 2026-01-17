from django.contrib import admin
from django.urls import path, include

from apps.api import urls as api_urls
from apps.login import urls as login_urls
from apps.dashboard import urls as dashboard_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include(api_urls)),
    path("", include(login_urls)),
    path("dashboard/", include(dashboard_urls)),
]
