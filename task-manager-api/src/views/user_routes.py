from flask import Blueprint, jsonify, request

from src.middlewares.auth import current_actor_id
from src.views.presenters import present_task, present_user, present_user_summary, present_user_task


def create_user_blueprint(controller):
    bp = Blueprint('users', __name__)

    @bp.get('/users')
    def get_users():
        return jsonify([present_user_summary(u, count) for u, count in controller.list_users()]), 200

    @bp.get('/users/<int:user_id>')
    def get_user(user_id):
        user, tasks = controller.get_user_with_tasks(user_id)
        return jsonify({**present_user(user), 'tasks': [present_task(t) for t in tasks]}), 200

    @bp.post('/users')
    def create_user():
        user = controller.create_user(request.get_json(), current_actor_id())
        return jsonify(present_user(user)), 201

    @bp.put('/users/<int:user_id>')
    def update_user(user_id):
        user = controller.update_user(user_id, request.get_json(), current_actor_id())
        return jsonify(present_user(user)), 200

    @bp.delete('/users/<int:user_id>')
    def delete_user(user_id):
        controller.delete_user(user_id, current_actor_id())
        return jsonify({'message': 'Usuário deletado com sucesso'}), 200

    @bp.get('/users/<int:user_id>/tasks')
    def get_user_tasks(user_id):
        _, tasks = controller.get_user_with_tasks(user_id)
        return jsonify([present_user_task(t) for t in tasks]), 200

    @bp.post('/login')
    def login():
        user, token = controller.login(request.get_json())
        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': present_user(user),
            'token': token,
        }), 200

    return bp
