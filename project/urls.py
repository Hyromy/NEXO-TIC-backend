from django.contrib import admin
from django.urls import path, include

from apps.api import urls as api_urls
from apps.authentication import urls as auth_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include(api_urls)),
    path("auth/", include(auth_urls)),
]
