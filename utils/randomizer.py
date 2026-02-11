import random

def generate_password(*,
    size: int = 8,
    use_upper: bool = False,
    use_numbers: bool = False,
    use_special_chars: bool | str = False
) -> str:
    """Generates a random password."""

    letters = [chr(i) for i in range(ord('a'), ord('z') + 1)]
    numbers = [str(i) for i in range(0, 10)]
    special_chars = []
    if isinstance(use_special_chars, str):
        special_chars = list(use_special_chars)
    elif isinstance(use_special_chars, bool) and use_special_chars:
        special_chars = list("!@#$%^&*()_-+=")

    available = letters[:]
    if use_upper:
        available += [ch.upper() for ch in letters]
    if use_numbers:
        available += numbers
    if use_special_chars:
        available += special_chars

    return ''.join(random.choice(available) for _ in range(size))
