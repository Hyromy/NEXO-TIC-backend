from django.urls import path

from .views import (
    login,
    logout,
    signup,
)

urlpatterns = [
    path("", login, name = "login"),
    path("logout/", logout, name = "logout"),
    path("signup/", signup, name = "signup"),
]
