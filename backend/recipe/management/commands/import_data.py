import json

from django.core.management.base import BaseCommand
from django.conf import settings

from recipe.models import Ingredient, Tag


class BaseImportCommand(BaseCommand):
    """Базовый класс для команд импорта из JSON файлов."""

    def load_data(self, file_path):
        """Метод для загрузки данных из файла."""
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data


class ImportDataCommand(BaseImportCommand):
    """Команда для импорта ингредиентов и тегов из JSON файлов."""

    help = 'Импорт продуктов и тегов из JSON файлов'

    def handle(self, *args, **kwargs):
        ingredients_file_path = settings.BASE_DIR / 'data' / 'ingredients.json'
        ingredients_data = self.load_data(ingredients_file_path)
        Ingredient.objects.bulk_create(
            (Ingredient(**item) for item in ingredients_data),
            ignore_conflicts=True
        )
        tags_file_path = settings.BASE_DIR / 'data' / 'tags.json'
        tags_data = self.load_data(tags_file_path)
        Tag.objects.bulk_create(
            (Tag(**item) for item in tags_data),
            ignore_conflicts=True
        )
        self.stdout.write(
            self.style.SUCCESS('Ингредиенты и теги успешно импортированы.')
        )
