from django.urls import path

from .views import (
    MyTokenObtainPairView,
    MyTokenRefreshView,
    signup,
    logout,
)

urlpatterns = [
    path("signup/", signup),                            # public
    path("login/", MyTokenObtainPairView.as_view()),    # public
    path("refresh/", MyTokenRefreshView.as_view()),     # public
    path("logout/", logout),
]
