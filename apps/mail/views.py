from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpRequest

def welcome(request: HttpRequest, user: User, /):
    send_mail(
        subject = "Bienvenido a NexoTic",
        message = "Gracias por registrarte en nuestro sistema.",
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [user.email],
        fail_silently = False
    )
