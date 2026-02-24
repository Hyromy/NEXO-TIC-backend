from django.urls import path

from .views import (
    MyTokenObtainPairView,
    MyTokenRefreshView,
    signup,
    logout,
    recover,
    reset_password,
)

urlpatterns = [
    path("signup/", signup),                            # public
    path("login/", MyTokenObtainPairView.as_view()),    # public
    path("refresh/", MyTokenRefreshView.as_view()),     # public
    path("recover/", recover),                          # public
    path("logout/", logout),
    path("reset-password/", reset_password)
]
