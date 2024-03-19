import string
from secrets import choice as secrets_choice


async def generate_random_string():
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets_choice(alphabet) for _ in range(16))


async def send_temp_password_at_email(email: str, password: str):
    """
    This is function for mocking email notifications
    :param email:
    :param password:
    :return:
    """
    return f"Password ({password}) send at {email} address"
