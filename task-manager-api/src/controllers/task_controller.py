import logging

from src.controllers import validators as v
from src.database.connection import commit
from src.middlewares.error_handler import NotFoundError
from src.models.category_model import Category
from src.models.clock import utc_now
from src.models.constants import DEFAULT_PRIORITY, DEFAULT_STATUS, STATUS_DONE, TASK_STATUSES
from src.models.task_model import Task
from src.models.user_model import User

logger = logging.getLogger(__name__)

TASK_NOT_FOUND = 'Task não encontrada'
DUE_DATE_ERROR_ON_CREATE = 'Formato de data inválido. Use YYYY-MM-DD'
DUE_DATE_ERROR_ON_UPDATE = 'Formato de data inválido'


def completion_rate(done, total):
    return round((done / total) * 100, 2) if total > 0 else 0


class TaskController:
    def list_tasks(self):
        return Task.list_with_relations()

    def get_task(self, task_id):
        task = Task.find_by_id(task_id)
        if not task:
            raise NotFoundError(TASK_NOT_FOUND)
        return task

    def create_task(self, data):
        v.require_payload(data)
        title = v.validate_title(data.get('title'), required=True)
        description = v.validate_optional_text(data.get('description', ''), 'description')
        status = v.validate_status(data.get('status', DEFAULT_STATUS))
        priority = v.validate_priority(data.get('priority', DEFAULT_PRIORITY))
        user_id = v.validate_optional_id(data.get('user_id'), 'user_id')
        category_id = v.validate_optional_id(data.get('category_id'), 'category_id')
        self._ensure_references(user_id, category_id)

        task = Task(title=title, description=description, status=status, priority=priority,
                    user_id=user_id, category_id=category_id)
        if data.get('due_date'):
            task.due_date = v.validate_due_date(data['due_date'], DUE_DATE_ERROR_ON_CREATE)
        if data.get('tags'):
            task.tags = v.normalize_tags(data['tags'])

        task.save()
        commit()
        logger.info('Task criada: %s', task.id)
        return task

    def update_task(self, task_id, data):
        task = self.get_task(task_id)
        v.require_payload(data)

        if 'title' in data:
            task.title = v.validate_title(data['title'], required=False)
        if 'description' in data:
            task.description = v.validate_optional_text(data['description'], 'description')
        if 'status' in data:
            task.status = v.validate_status(data['status'])
        if 'priority' in data:
            task.priority = v.validate_priority(data['priority'])
        if 'user_id' in data:
            user_id = v.validate_optional_id(data['user_id'], 'user_id')
            self._ensure_references(user_id, None)
            task.user_id = user_id
        if 'category_id' in data:
            category_id = v.validate_optional_id(data['category_id'], 'category_id')
            self._ensure_references(None, category_id)
            task.category_id = category_id
        if 'due_date' in data:
            due_date = data['due_date']
            task.due_date = v.validate_due_date(due_date, DUE_DATE_ERROR_ON_UPDATE) if due_date else None
        if 'tags' in data:
            task.tags = v.normalize_tags(data['tags']) if data['tags'] is not None else None

        task.updated_at = utc_now()
        commit()
        logger.info('Task atualizada: %s', task.id)
        return task

    def delete_task(self, task_id):
        task = self.get_task(task_id)
        task.delete()
        commit()
        logger.info('Task deletada: %s', task_id)

    def search_tasks(self, text, status, priority, user_id):
        return Task.search(
            text=text or None,
            status=status or None,
            priority=v.parse_int(priority, 'Prioridade inválida') if priority else None,
            user_id=v.parse_int(user_id, 'user_id inválido') if user_id else None,
        )

    def stats(self):
        total = Task.count()
        by_status = Task.count_by_status()
        done = by_status.get(STATUS_DONE, 0)
        stats = {status: by_status.get(status, 0) for status in TASK_STATUSES}
        stats.update({
            'total': total,
            'overdue': Task.count(Task.overdue_clause(utc_now())),
            'completion_rate': completion_rate(done, total),
        })
        return stats

    @staticmethod
    def _ensure_references(user_id, category_id):
        if user_id and not User.find_by_id(user_id):
            raise NotFoundError('Usuário não encontrado')
        if category_id and not Category.find_by_id(category_id):
            raise NotFoundError('Categoria não encontrada')
