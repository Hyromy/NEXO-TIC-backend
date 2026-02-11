import re

def is_email(value: str) -> bool:
    """Check if the provided value is a valid email address."""
    
    email_regex = r'^[a-zA-Z][a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.)+[a-z]{2,}$'
    return re.match(email_regex, value) is not None
