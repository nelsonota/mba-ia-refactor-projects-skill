from flask import Blueprint, jsonify
from src.controllers.task_controller import TaskController
from src.views.validation import read_json_object, read_task_search_args

task_bp = Blueprint('tasks', __name__)

@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    payload, status = TaskController.get_tasks()
    return jsonify(payload), status

@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    payload, status = TaskController.get_task(task_id)
    return jsonify(payload), status

@task_bp.route('/tasks', methods=['POST'])
def create_task():
    payload, status = TaskController.create_task(data=read_json_object('task'))
    return jsonify(payload), status

@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    payload, status = TaskController.update_task(task_id, data=read_json_object('task'))
    return jsonify(payload), status

@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    payload, status = TaskController.delete_task(task_id)
    return jsonify(payload), status

@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    payload, status = TaskController.search_tasks(query_args=read_task_search_args())
    return jsonify(payload), status

@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    payload, status = TaskController.task_stats()
    return jsonify(payload), status
