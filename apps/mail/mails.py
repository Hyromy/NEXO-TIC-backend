import logging

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from requests import get

logger = logging.getLogger(__name__)
    
def __create_user_inbox(*, user: User) -> bool:
    user_name = user.email.split("@")[0]
    url = f"http://mail.nexotic.com/create_mailbox.php?user={user_name}"
    r = get(url, timeout = 5)
    
    return r.text == "ok"

def __safe_send(user: User, *,
    subject: str = "{{ No subject }}",
    summary: str = "{{ No summary }}",
    message: str = "{{ No message }}",
    template: str | None = None
):
    if settings.DEBUG:
        bar = "="
        bar_size = 12
        header = f"{bar * bar_size} NEW MAIL {bar * bar_size}"
        
        logger.info(header)
        logger.info(f"Subject: {subject}")
        logger.info(f"To: {user.email}")
        logger.info(f"Summary: {summary}")
        logger.info(bar * len(header))
        
        return
    
    try:
        send_mail(
            subject = subject,
            message = message,
            from_email = settings.DEFAULT_FROM_EMAIL,
            recipient_list = [user.email],
            fail_silently = False,
            html_message = template
        )

    except Exception as e:
        logger.error(f"Error sending email to {user.email}: {e}")
        raise e

def welcome(*, user: User, tmp_pass: str):
    if not settings.DEBUG:
        __create_user_inbox(user = user)

    __safe_send(user,
        subject = "Bienvenido a NexoTic",
        summary = f"Registro exitoso, contraseña temporal {tmp_pass}",
        template = render_to_string("mail/welcome.html", {
            "user": user,
            "tmp_pass": tmp_pass
        })
    )

def recover(*, user: User, tmp_pass: str):
    __safe_send(user,
        subject = "Recuperación de contraseña",
        summary = f"Contraseña temporal {tmp_pass}",
        template = render_to_string("mail/recover.html", {
            "user": user,
            "tmp_pass": tmp_pass
        })
    )
