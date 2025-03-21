import os
from hashlib import blake2b

# from django.conf import settings

from foodgram_backend.constants import DIGEST_SIZE


def generate_short_url(url):
    domain = os.getenv('DOMAIN', 'localhost')
    base_url = f'https://{domain}/'
    hash_url = blake2b(url.encode(), digest_size=DIGEST_SIZE).hexdigest()
    return f'{base_url}{hash_url}'

# def generate_short_url(request):
#     """Метод для получения URL текущей страницы."""
#     current_url = request.build_absolute_uri()
#     return current_url
