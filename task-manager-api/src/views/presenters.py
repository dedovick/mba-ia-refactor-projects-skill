"""Formato das respostas. Cada presenter usa uma whitelist de campos (senha nunca sai)."""


def _format_datetime(value):
    return str(value) if value else None


def present_user(user):
    return {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'active': user.active,
        'created_at': str(user.created_at),
    }


def present_user_summary(user, task_count):
    return {**present_user(user), 'task_count': task_count}


def present_task(task):
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'user_id': task.user_id,
        'category_id': task.category_id,
        'created_at': str(task.created_at),
        'updated_at': str(task.updated_at),
        'due_date': _format_datetime(task.due_date),
        'tags': task.tag_list,
    }


def present_task_detail(task):
    return {**present_task(task), 'overdue': task.is_overdue()}


def present_task_list_item(task):
    return {
        **present_task_detail(task),
        'user_name': task.user.name if task.user else None,
        'category_name': task.category.name if task.category else None,
    }


def present_user_task(task):
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'created_at': str(task.created_at),
        'due_date': _format_datetime(task.due_date),
        'overdue': task.is_overdue(),
    }


def present_category(category):
    return {
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'color': category.color,
        'created_at': str(category.created_at),
    }


def present_category_summary(category, task_count):
    return {**present_category(category), 'task_count': task_count}
