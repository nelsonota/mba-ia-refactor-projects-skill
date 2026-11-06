from src.errors import ServiceOperationError
from src.services.clock import utc_now
from database import db
from models.user import User
from models.task import Task
import re
from src.models.constants import DEFAULT_USER_ROLE, VALID_USER_ROLES, MIN_PASSWORD_LENGTH, STATUS_DONE, STATUS_CANCELLED

def _response_payload(value):
    return value

def get_users(data=None, query_args=None):
    users = User.query.all()
    task_counts = dict(db.session.query(Task.user_id, db.func.count(Task.id)).group_by(Task.user_id).all())
    result = []
    for user in users:
        user_data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'active': user.active,
            'created_at': str(user.created_at),
            'task_count': task_counts.get(user.id, 0)
        }
        result.append(user_data)
    return _response_payload(result), 200

def get_user(user_id, data=None, query_args=None):
    user = User.query.get(user_id)
    if not user:
        return _response_payload({'error': 'UsuÃ¡rio nÃ£o encontrado'}), 404
    data = user.to_dict()
    tasks = Task.query.filter_by(user_id=user_id).all()
    data['tasks'] = []
    for task in tasks:
        data['tasks'].append(task.to_dict())
    return _response_payload(data), 200

def create_user(data=None, query_args=None):
    if not data:
        return _response_payload({'error': 'Dados invÃ¡lidos'}), 400
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', DEFAULT_USER_ROLE)
    if not name:
        return _response_payload({'error': 'Nome Ã© obrigatÃ³rio'}), 400
    if not email:
        return _response_payload({'error': 'Email Ã© obrigatÃ³rio'}), 400
    if not password:
        return _response_payload({'error': 'Senha Ã© obrigatÃ³ria'}), 400
    if not re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', email):
        return _response_payload({'error': 'Email invÃ¡lido'}), 400
    if len(password) < MIN_PASSWORD_LENGTH:
        return _response_payload({'error': 'Senha deve ter no mÃ­nimo 4 caracteres'}), 400
    existing = User.query.filter_by(email=email).first()
    if existing:
        return _response_payload({'error': 'Email jÃ¡ cadastrado'}), 409
    if role not in VALID_USER_ROLES:
        return _response_payload({'error': 'Role invÃ¡lido'}), 400
    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role
    try:
        db.session.add(user)
        db.session.commit()
        print(f"UsuÃ¡rio criado: {user.id} - {user.name}")

        response_data = user.to_dict()
        return _response_payload(response_data), 201
    except Exception as error:
        db.session.rollback()
        raise ServiceOperationError('Erro ao criar usu\u00e1rio') from error

def update_user(user_id, data=None, query_args=None):
    user = User.query.get(user_id)
    if not user:
        return _response_payload({'error': 'UsuÃ¡rio nÃ£o encontrado'}), 404
    if not data:
        return _response_payload({'error': 'Dados invÃ¡lidos'}), 400
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        if not re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', data['email']):
            return _response_payload({'error': 'Email invÃ¡lido'}), 400

        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            return _response_payload({'error': 'Email jÃ¡ cadastrado'}), 409
        user.email = data['email']
    if 'password' in data:
        if len(data['password']) < MIN_PASSWORD_LENGTH:
            return _response_payload({'error': 'Senha muito curta'}), 400
        user.set_password(data['password'])
    if 'role' in data:
        if data['role'] not in VALID_USER_ROLES:
            return _response_payload({'error': 'Role invÃ¡lido'}), 400
        user.role = data['role']
    if 'active' in data:
        user.active = data['active']
    try:
        db.session.commit()
        return _response_payload(user.to_dict()), 200
    except Exception as error:
        db.session.rollback()
        raise ServiceOperationError('Erro ao atualizar') from error

def delete_user(user_id, data=None, query_args=None):
    user = User.query.get(user_id)
    if not user:
        return _response_payload({'error': 'UsuÃ¡rio nÃ£o encontrado'}), 404
    tasks = Task.query.filter_by(user_id=user_id).all()
    for task in tasks:
        db.session.delete(task)
    try:
        db.session.delete(user)
        db.session.commit()
        print(f"UsuÃ¡rio deletado: {user_id}")
        return _response_payload({'message': 'UsuÃ¡rio deletado com sucesso'}), 200
    except Exception as error:
        db.session.rollback()
        raise ServiceOperationError('Erro ao deletar') from error

def get_user_tasks(user_id, data=None, query_args=None):
    user = User.query.get(user_id)
    if not user:
        return _response_payload({'error': 'UsuÃ¡rio nÃ£o encontrado'}), 404
    tasks = Task.query.filter_by(user_id=user_id).all()
    result = []
    for task in tasks:
        task_data = {}
        task_data['id'] = task.id
        task_data['title'] = task.title
        task_data['description'] = task.description
        task_data['status'] = task.status
        task_data['priority'] = task.priority
        task_data['created_at'] = str(task.created_at)
        task_data['due_date'] = str(task.due_date) if task.due_date else None

        if task.due_date:
            if task.due_date < utc_now():
                if task.status != STATUS_DONE and task.status != STATUS_CANCELLED:
                    task_data['overdue'] = True
                else:
                    task_data['overdue'] = False
            else:
                task_data['overdue'] = False
        else:
            task_data['overdue'] = False
        result.append(task_data)
    return _response_payload(result), 200
