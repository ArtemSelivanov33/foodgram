from hashlib import blake2b

from django.conf import settings

from foodgram_backend.constants import DIGEST_SIZE


def generate_short_url(url):
    base_url = f'https://{settings.ALLOWED_HOSTS[0]}/s/'
    hash_url = blake2b(url.encode(), digest_size=DIGEST_SIZE).hexdigest()
    return f'{base_url}{hash_url}'
