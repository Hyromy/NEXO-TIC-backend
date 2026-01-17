from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import (
    authenticate,
    login as auth_login,
    logout as auth_logout,
)
from django.contrib.auth.models import User

def login(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        user_name = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username = user_name, password = password)
        if user:
            auth_login(request, user)
            return redirect("dashboard")
        
        return render(request, "login.html", {
            "error": "Credenciales inválidas. Por favor, inténtalo de nuevo."
        })

    return render(request, "login.html")

def __check_signup(user_name, email, password, confirm_password) -> str | None:
    if password != confirm_password:
        return "Las contraseñas no coinciden. Por favor, inténtalo de nuevo."
    if User.objects.filter(username = user_name).exists():
        return "El nombre de usuario ya existe. Por favor, elige otro."
    if User.objects.filter(email = email).exists():
        return "El correo electrónico ya está registrado. Por favor, usa otro."


def signup(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        user_name = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        fail = __check_signup(user_name, email, password, confirm_password)
        if fail is not None:
            return render(request, "signup.html", {
                "error": fail
            })

        try:
            user = User.objects.create_user(username = user_name, email = email, password = password)
            auth_login(request, user)
        
        except Exception as e:
            return render(request, "signup.html", {
                "error": f"Ocurrió un error al crear la cuenta: {str(e)}"
            })
        
        else:
            return redirect("dashboard")

    return render(request, "signup.html")

def logout(request: HttpRequest) -> HttpResponse:
    auth_logout(request)
    return redirect("login")
