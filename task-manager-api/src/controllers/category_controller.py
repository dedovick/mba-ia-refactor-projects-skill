from src.controllers import validators as v
from src.database.connection import commit
from src.middlewares.error_handler import NotFoundError, ValidationError
from src.models.category_model import Category
from src.models.constants import DEFAULT_COLOR
from src.models.task_model import Task

CATEGORY_NOT_FOUND = 'Categoria não encontrada'


class CategoryController:
    def list_categories(self):
        counts = Task.count_by_category()
        return [(category, counts.get(category.id, 0)) for category in Category.list_all()]

    def get_category(self, category_id):
        category = Category.find_by_id(category_id)
        if not category:
            raise NotFoundError(CATEGORY_NOT_FOUND)
        return category

    def create_category(self, data):
        v.require_payload(data)
        name = data.get('name')
        if not name:
            raise ValidationError('Nome é obrigatório')
        category = Category(
            name=v.validate_name(name),
            description=v.validate_optional_text(data.get('description', ''), 'description'),
            color=v.validate_color(data.get('color', DEFAULT_COLOR)),
        )
        category.save()
        commit()
        return category

    def update_category(self, category_id, data):
        category = self.get_category(category_id)
        v.require_object(data)
        if 'name' in data:
            category.name = v.validate_name(data['name'])
        if 'description' in data:
            category.description = v.validate_optional_text(data['description'], 'description')
        if 'color' in data:
            category.color = v.validate_color(data['color'])
        commit()
        return category

    def delete_category(self, category_id):
        category = self.get_category(category_id)
        category.delete()  # o ORM desvincula as tasks (category_id = NULL)
        commit()
