import random
import string


def generate_random_string(n):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))
