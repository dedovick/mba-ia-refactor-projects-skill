from datetime import timedelta

from src.controllers.task_controller import completion_rate
from src.middlewares.error_handler import NotFoundError
from src.models.category_model import Category
from src.models.clock import utc_now
from src.models.constants import (
    HIGH_PRIORITY_MAX,
    PRIORITY_LABELS,
    RECENT_ACTIVITY_DAYS,
    STATUS_DONE,
    TASK_STATUSES,
)
from src.models.task_model import Task
from src.models.user_model import User


class ReportController:
    def summary(self):
        now = utc_now()
        since = now - timedelta(days=RECENT_ACTIVITY_DAYS)
        by_status = Task.count_by_status()
        by_priority = Task.count_by_priority()
        overdue = Task.list_overdue(now)

        return {
            'generated_at': str(now),
            'overview': {
                'total_tasks': Task.count(),
                'total_users': User.count(),
                'total_categories': Category.count(),
            },
            'tasks_by_status': {status: by_status.get(status, 0) for status in TASK_STATUSES},
            'tasks_by_priority': {label: by_priority.get(priority, 0) for priority, label in PRIORITY_LABELS.items()},
            'overdue': {
                'count': len(overdue),
                'tasks': [
                    {
                        'id': task.id,
                        'title': task.title,
                        'due_date': str(task.due_date),
                        'days_overdue': (now - task.due_date).days,
                    }
                    for task in overdue
                ],
            },
            'recent_activity': {
                'tasks_created_last_7_days': Task.count(Task.created_at >= since),
                'tasks_completed_last_7_days': Task.count(Task.status == STATUS_DONE, Task.updated_at >= since),
            },
            'user_productivity': self._user_productivity(),
        }

    def user_report(self, user_id):
        user = User.find_by_id(user_id)
        if not user:
            raise NotFoundError('Usuário não encontrado')

        now = utc_now()
        tasks = Task.list_by_user(user_id)
        by_status = {status: 0 for status in TASK_STATUSES}
        for task in tasks:
            if task.status in by_status:
                by_status[task.status] += 1
        total = len(tasks)

        return {
            'user': {'id': user.id, 'name': user.name, 'email': user.email},
            'statistics': {
                'total_tasks': total,
                **by_status,
                'overdue': sum(1 for task in tasks if task.is_overdue(now)),
                'high_priority': sum(1 for task in tasks if task.priority <= HIGH_PRIORITY_MAX),
                'completion_rate': completion_rate(by_status[STATUS_DONE], total),
            },
        }

    @staticmethod
    def _user_productivity():
        totals = Task.count_by_user()
        completed = Task.count_done_by_user()
        stats = []
        for user in User.list_all():
            total = totals.get(user.id, 0)
            done = completed.get(user.id, 0)
            stats.append({
                'user_id': user.id,
                'user_name': user.name,
                'total_tasks': total,
                'completed_tasks': done,
                'completion_rate': completion_rate(done, total),
            })
        return stats
