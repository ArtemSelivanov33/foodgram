import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework.serializers import ImageField


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, image = data.split(';base64,')
            data = ContentFile(
                base64.b64decode(image), name=f'{uuid.uuid4()}.jpg'
            )
        return super().to_internal_value(data)