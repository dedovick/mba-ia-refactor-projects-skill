from flask import Blueprint, jsonify, request

from src.views.presenters import present_category, present_category_summary


def create_category_blueprint(controller):
    bp = Blueprint('categories', __name__)

    @bp.get('/categories')
    def get_categories():
        return jsonify([present_category_summary(c, count) for c, count in controller.list_categories()]), 200

    @bp.post('/categories')
    def create_category():
        return jsonify(present_category(controller.create_category(request.get_json()))), 201

    @bp.put('/categories/<int:category_id>')
    def update_category(category_id):
        return jsonify(present_category(controller.update_category(category_id, request.get_json()))), 200

    @bp.delete('/categories/<int:category_id>')
    def delete_category(category_id):
        controller.delete_category(category_id)
        return jsonify({'message': 'Categoria deletada'}), 200

    return bp
