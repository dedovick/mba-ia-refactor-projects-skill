from flask import Blueprint, jsonify, request

from src.views.presenters import present_task, present_task_detail, present_task_list_item


def create_task_blueprint(controller):
    bp = Blueprint('tasks', __name__)

    @bp.get('/tasks')
    def get_tasks():
        return jsonify([present_task_list_item(t) for t in controller.list_tasks()]), 200

    @bp.get('/tasks/<int:task_id>')
    def get_task(task_id):
        return jsonify(present_task_detail(controller.get_task(task_id))), 200

    @bp.post('/tasks')
    def create_task():
        return jsonify(present_task(controller.create_task(request.get_json()))), 201

    @bp.put('/tasks/<int:task_id>')
    def update_task(task_id):
        return jsonify(present_task(controller.update_task(task_id, request.get_json()))), 200

    @bp.delete('/tasks/<int:task_id>')
    def delete_task(task_id):
        controller.delete_task(task_id)
        return jsonify({'message': 'Task deletada com sucesso'}), 200

    @bp.get('/tasks/search')
    def search_tasks():
        args = request.args
        tasks = controller.search_tasks(args.get('q', ''), args.get('status', ''),
                                        args.get('priority', ''), args.get('user_id', ''))
        return jsonify([present_task(t) for t in tasks]), 200

    @bp.get('/tasks/stats')
    def task_stats():
        return jsonify(controller.stats()), 200

    return bp
