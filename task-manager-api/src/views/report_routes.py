from flask import Blueprint, jsonify
from src.controllers.report_controller import ReportController
from src.views.validation import read_json_object

report_bp = Blueprint('reports', __name__)

@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    payload, status = ReportController.summary_report()
    return jsonify(payload), status

@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    payload, status = ReportController.user_report(user_id)
    return jsonify(payload), status

@report_bp.route('/categories', methods=['GET'])
def get_categories():
    payload, status = ReportController.get_categories()
    return jsonify(payload), status

@report_bp.route('/categories', methods=['POST'])
def create_category():
    payload, status = ReportController.create_category(data=read_json_object('category'))
    return jsonify(payload), status

@report_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    payload, status = ReportController.update_category(category_id, data=read_json_object('category'))
    return jsonify(payload), status

@report_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    payload, status = ReportController.delete_category(category_id)
    return jsonify(payload), status
