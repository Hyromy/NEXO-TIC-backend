from django.contrib.auth.models import User
from requests import get

def create_user_inbox(user: User) -> bool:
    user_name = user.email.split("@")[0]
    url = f"http://mail.nexotic.com/create_mailbox.php?user={user_name}"
    r = get(url, timeout = 5)
    
    print(r.text)

    return r.text == "ok"
