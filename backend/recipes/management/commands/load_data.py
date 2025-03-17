import json

from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from foodgram_backend.settings import PATH_TO_INGREDIENTS
from recipes.models import Ingredient


class Command(BaseCommand):
    """Заполнение базы ингридиентами"""

    def handle(self, *args, **options):

        with open(PATH_TO_INGREDIENTS, encoding='UTF-8') as ingredients_file:
            ingredients = json.load(ingredients_file)

            for ingredient in tqdm(ingredients):
                try:
                    Ingredient.objects.get_or_create(**ingredient)
                except CommandError as e:
                    raise CommandError(
                        f'При добавлении {ingredient} '
                        f'произшла ошибка {e}'
                    )
