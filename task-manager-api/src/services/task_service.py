from src.errors import ServiceOperationError
from src.services.clock import utc_now
from database import db
from models.task import Task
from models.user import User
from models.category import Category
from datetime import datetime
from sqlalchemy.orm import joinedload
from src.models.constants import VALID_TASK_STATUSES, STATUS_PENDING, STATUS_IN_PROGRESS, MIN_TASK_PRIORITY, MAX_TASK_PRIORITY, DEFAULT_TASK_PRIORITY, MIN_TASK_TITLE_LENGTH, MAX_TASK_TITLE_LENGTH, STATUS_DONE, STATUS_CANCELLED, PRIORITY_CRITICAL, PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_LOW, PRIORITY_MINIMAL

def _response_payload(value):
    return value

def get_tasks(data=None, query_args=None):
    tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
    result = []
    for task in tasks:
        task_data = {}
        task_data['id'] = task.id
        task_data['title'] = task.title
        task_data['description'] = task.description
        task_data['status'] = task.status
        task_data['priority'] = task.priority
        task_data['user_id'] = task.user_id
        task_data['category_id'] = task.category_id
        task_data['created_at'] = str(task.created_at)
        task_data['updated_at'] = str(task.updated_at)
        task_data['due_date'] = str(task.due_date) if task.due_date else None
        task_data['tags'] = task.tags.split(',') if task.tags else []

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

        if task.user_id:
            user = task.user
            if user:
                task_data['user_name'] = user.name
            else:
                task_data['user_name'] = None
        else:
            task_data['user_name'] = None

        if task.category_id:
            category = task.category
            if category:
                task_data['category_name'] = category.name
            else:
                task_data['category_name'] = None
        else:
            task_data['category_name'] = None

        result.append(task_data)

    return _response_payload(result), 200
def get_task(task_id, data=None, query_args=None):
    task = Task.query.get(task_id)
    if task:
        data = task.to_dict()

        if task.due_date:
            if task.due_date < utc_now():
                if task.status != STATUS_DONE and task.status != STATUS_CANCELLED:
                    data['overdue'] = True
                else:
                    data['overdue'] = False
            else:
                data['overdue'] = False
        else:
            data['overdue'] = False
        return _response_payload(data), 200
    else:
        return _response_payload({'error': 'Task nÃ£o encontrada'}), 404

def create_task(data=None, query_args=None):
    if not data:
        return _response_payload({'error': 'Dados invÃ¡lidos'}), 400
    title = data.get('title')
    if not title:
        return _response_payload({'error': 'TÃ­tulo Ã© obrigatÃ³rio'}), 400
    if len(title) < MIN_TASK_TITLE_LENGTH:
        return _response_payload({'error': 'TÃ­tulo muito curto'}), 400
    if len(title) > MAX_TASK_TITLE_LENGTH:
        return _response_payload({'error': 'TÃ­tulo muito longo'}), 400
    description = data.get('description', '')
    status = data.get('status', STATUS_PENDING)
    priority = data.get('priority', DEFAULT_TASK_PRIORITY)
    user_id = data.get('user_id')
    category_id = data.get('category_id')
    due_date = data.get('due_date')
    tags = data.get('tags')
    if status not in VALID_TASK_STATUSES:
        return _response_payload({'error': 'Status invÃ¡lido'}), 400
    if priority < MIN_TASK_PRIORITY or priority > MAX_TASK_PRIORITY:
        return _response_payload({'error': 'Prioridade deve ser entre 1 e 5'}), 400
    if user_id:
        user = User.query.get(user_id)
        if not user:
            return _response_payload({'error': 'UsuÃ¡rio nÃ£o encontrado'}), 404
    if category_id:
        category = Category.query.get(category_id)
        if not category:
            return _response_payload({'error': 'Categoria nÃ£o encontrada'}), 404
    task = Task()
    task.title = title
    task.description = description
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id
    if due_date:
        try:
            task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            return _response_payload({'error': 'Formato de data invÃ¡lido. Use YYYY-MM-DD'}), 400
    if tags:
        if type(tags) == list:
            task.tags = ','.join(tags)
        else:
            task.tags = tags
    try:
        db.session.add(task)
        db.session.commit()
        print(f"Task criada: {task.id} - {task.title}")
        return _response_payload(task.to_dict()), 201
    except Exception as error:
        db.session.rollback()
        raise ServiceOperationError('Erro ao criar task') from error

def update_task(task_id, data=None, query_args=None):
    task = Task.query.get(task_id)
    if not task:
        return _response_payload({'error': 'Task nÃ£o encontrada'}), 404
    if not data:
        return _response_payload({'error': 'Dados invÃ¡lidos'}), 400
    if 'title' in data:
        if len(data['title']) < MIN_TASK_TITLE_LENGTH:
            return _response_payload({'error': 'TÃ­tulo muito curto'}), 400
        if len(data['title']) > MAX_TASK_TITLE_LENGTH:
            return _response_payload({'error': 'TÃ­tulo muito longo'}), 400
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        if data['status'] not in VALID_TASK_STATUSES:
            return _response_payload({'error': 'Status invÃ¡lido'}), 400
        task.status = data['status']
    if 'priority' in data:
        if data['priority'] < MIN_TASK_PRIORITY or data['priority'] > MAX_TASK_PRIORITY:
            return _response_payload({'error': 'Prioridade deve ser entre 1 e 5'}), 400
        task.priority = data['priority']
    if 'user_id' in data:
        if data['user_id']:
            user = User.query.get(data['user_id'])
            if not user:
                return _response_payload({'error': 'UsuÃ¡rio nÃ£o encontrado'}), 404
        task.user_id = data['user_id']
    if 'category_id' in data:
        if data['category_id']:
            category = Category.query.get(data['category_id'])
            if not category:
                return _response_payload({'error': 'Categoria nÃ£o encontrada'}), 404
        task.category_id = data['category_id']
    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
            except ValueError:
                return _response_payload({'error': 'Formato de data invÃ¡lido'}), 400
        else:
            task.due_date = None
    if 'tags' in data:
        if type(data['tags']) == list:
            task.tags = ','.join(data['tags'])
        else:
            task.tags = data['tags']
    task.updated_at = utc_now()
    try:
        db.session.commit()
        print(f"Task atualizada: {task.id}")
        return _response_payload(task.to_dict()), 200
    except Exception as error:
        db.session.rollback()
        raise ServiceOperationError('Erro ao atualizar') from error

def delete_task(task_id, data=None, query_args=None):
    task = Task.query.get(task_id)
    if not task:
        return _response_payload({'error': 'Task nÃ£o encontrada'}), 404
    try:
        db.session.delete(task)
        db.session.commit()
        print(f"Task deletada: {task_id}")
        return _response_payload({'message': 'Task deletada com sucesso'}), 200
    except Exception as error:
        db.session.rollback()
        raise ServiceOperationError('Erro ao deletar') from error

def search_tasks(data=None, query_args=None):
    query_args = query_args or {}
    query = query_args.get('q', '')
    status = query_args.get('status', '')
    priority = query_args.get('priority', '')
    user_id = query_args.get('user_id', '')
    tasks = Task.query
    if query:
        tasks = tasks.filter(
            db.or_(
                Task.title.like(f'%{query}%'),
                Task.description.like(f'%{query}%')
            )
        )
    if status:
        tasks = tasks.filter(Task.status == status)
    if priority:
        tasks = tasks.filter(Task.priority == int(priority))
    if user_id:
        tasks = tasks.filter(Task.user_id == int(user_id))
    results = tasks.all()
    output = []
    for task in results:
        output.append(task.to_dict())
    return _response_payload(output), 200

def task_stats(data=None, query_args=None):
    total = Task.query.count()
    pending = Task.query.filter_by(status=STATUS_PENDING).count()
    in_progress = Task.query.filter_by(status=STATUS_IN_PROGRESS).count()
    done = Task.query.filter_by(status=STATUS_DONE).count()
    cancelled = Task.query.filter_by(status=STATUS_CANCELLED).count()
    current_time = utc_now()
    overdue_count = sum(1 for task in Task.query.all() if task.due_date and task.due_date < current_time and task.status not in (STATUS_DONE, STATUS_CANCELLED))
    return _response_payload({'total': total, 'pending': pending, 'in_progress': in_progress, 'done': done, 'cancelled': cancelled, 'overdue': overdue_count, 'completion_rate': round((done / total) * 100, 2) if total else 0}), 200
