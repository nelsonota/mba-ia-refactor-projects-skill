from flask import Blueprint, jsonify
from src.controllers.user_controller import UserController
from src.views.validation import read_json_object

user_bp = Blueprint('users', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    payload, status = UserController.get_users()
    return jsonify(payload), status

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    payload, status = UserController.get_user(user_id)
    return jsonify(payload), status

@user_bp.route('/users', methods=['POST'])
def create_user():
    payload, status = UserController.create_user(data=read_json_object('user'))
    return jsonify(payload), status

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    payload, status = UserController.update_user(user_id, data=read_json_object('user'))
    return jsonify(payload), status

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    payload, status = UserController.delete_user(user_id)
    return jsonify(payload), status

@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    payload, status = UserController.get_user_tasks(user_id)
    return jsonify(payload), status

@user_bp.route('/login', methods=['POST'])
def login():
    payload, status = UserController.login(data=read_json_object('user'))
    return jsonify(payload), status
