from src.errors import ServiceOperationError
from src.services.clock import utc_now
from database import db
from models.task import Task
from models.user import User
from models.category import Category
from datetime import timedelta
from src.models.constants import DEFAULT_CATEGORY_COLOR, STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_DONE, STATUS_CANCELLED, PRIORITY_CRITICAL, PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_LOW, PRIORITY_MINIMAL, HIGH_PRIORITY_MAX

def _response_payload(value):
    return value

def summary_report(data=None, query_args=None):
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()
    pending = Task.query.filter_by(status=STATUS_PENDING).count()
    in_progress = Task.query.filter_by(status=STATUS_IN_PROGRESS).count()
    done = Task.query.filter_by(status=STATUS_DONE).count()
    cancelled = Task.query.filter_by(status=STATUS_CANCELLED).count()
    priority_critical_count = Task.query.filter_by(priority=PRIORITY_CRITICAL).count()
    priority_high_count = Task.query.filter_by(priority=PRIORITY_HIGH).count()
    priority_medium_count = Task.query.filter_by(priority=PRIORITY_MEDIUM).count()
    priority_low_count = Task.query.filter_by(priority=PRIORITY_LOW).count()
    priority_minimal_count = Task.query.filter_by(priority=PRIORITY_MINIMAL).count()
    all_tasks = Task.query.all()
    overdue_count = 0
    overdue_list = []
    for task in all_tasks:
        if task.due_date:
            if task.due_date < utc_now():
                if task.status != STATUS_DONE and task.status != STATUS_CANCELLED:
                    overdue_count = overdue_count + 1
                    overdue_list.append({
                        'id': task.id,
                        'title': task.title,
                        'due_date': str(task.due_date),
                        'days_overdue': (utc_now() - task.due_date).days
                    })
    seven_days_ago = utc_now() - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == STATUS_DONE,
        Task.updated_at >= seven_days_ago
    ).count()
    users = User.query.all()
    task_stats_by_user = {}
    for task in all_tasks:
        user_task_statistics = task_stats_by_user.setdefault(task.user_id, [0, 0])
        user_task_statistics[0] += 1
        if task.status == STATUS_DONE:
            user_task_statistics[1] += 1
    user_stats = []
    for user in users:
        total, completed = task_stats_by_user.get(user.id, [0, 0])
        user_stats.append({
            'user_id': user.id,
            'user_name': user.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0
        })
    report = {
        'generated_at': str(utc_now()),
        'overview': {
            'total_tasks': total_tasks,
            'total_users': total_users,
            'total_categories': total_categories,
        },
        'tasks_by_status': {
            'pending': pending,
            'in_progress': in_progress,
            'done': done,
            'cancelled': cancelled,
        },
        'tasks_by_priority': {
            'critical': priority_critical_count,
            'high': priority_high_count,
            'medium': priority_medium_count,
            'low': priority_low_count,
            'minimal': priority_minimal_count,
        },
        'overdue': {
            'count': overdue_count,
            'tasks': overdue_list,
        },
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }
    return _response_payload(report), 200

def user_report(user_id, data=None, query_args=None):
    user = User.query.get(user_id)
    if not user:
        return _response_payload({'error': 'UsuÃ¡rio nÃ£o encontrado'}), 404
    tasks = Task.query.filter_by(user_id=user_id).all()
    total = len(tasks)
    done = 0
    pending = 0
    in_progress = 0
    cancelled = 0
    overdue = 0
    high_priority = 0
    for task in tasks:
        if task.status == STATUS_DONE:
            done = done + 1
        elif task.status == STATUS_PENDING:
            pending = pending + 1
        elif task.status == STATUS_IN_PROGRESS:
            in_progress = in_progress + 1
        elif task.status == STATUS_CANCELLED:
            cancelled = cancelled + 1

        if task.priority <= HIGH_PRIORITY_MAX:
            high_priority = high_priority + 1

        if task.due_date:
            if task.due_date < utc_now():
                if task.status != STATUS_DONE and task.status != STATUS_CANCELLED:
                    overdue = overdue + 1
    report = {
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        },
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': pending,
            'in_progress': in_progress,
            'cancelled': cancelled,
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0
        }
    }
    return _response_payload(report), 200

def get_categories(data=None, query_args=None):
    categories = Category.query.all()
    task_counts = dict(db.session.query(Task.category_id, db.func.count(Task.id)).group_by(Task.category_id).all())
    result = []
    for category in categories:
        category_data = category.to_dict()
        category_data['task_count'] = task_counts.get(category.id, 0)
        result.append(category_data)
    return _response_payload(result), 200

def create_category(data=None, query_args=None):
    if not data:
        return _response_payload({'error': 'Dados invÃ¡lidos'}), 400
    name = data.get('name')
    if not name:
        return _response_payload({'error': 'Nome Ã© obrigatÃ³rio'}), 400
    category = Category()
    category.name = name
    category.description = data.get('description', '')
    category.color = data.get('color', DEFAULT_CATEGORY_COLOR)
    try:
        db.session.add(category)
        db.session.commit()
        return _response_payload(category.to_dict()), 201
    except Exception as error:
        db.session.rollback()
        raise ServiceOperationError('Erro ao criar categoria') from error

def update_category(category_id, data=None, query_args=None):
    category = Category.query.get(category_id)
    if not category:
        return _response_payload({'error': 'Categoria nÃ£o encontrada'}), 404
    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']
    if 'color' in data:
        category.color = data['color']
    try:
        db.session.commit()
        return _response_payload(category.to_dict()), 200
    except Exception as error:
        db.session.rollback()
        raise ServiceOperationError('Erro ao atualizar') from error

def delete_category(category_id, data=None, query_args=None):
    category = Category.query.get(category_id)
    if not category:
        return _response_payload({'error': 'Categoria nÃ£o encontrada'}), 404
    try:
        db.session.delete(category)
        db.session.commit()
        return _response_payload({'message': 'Categoria deletada'}), 200
    except Exception as error:
        db.session.rollback()
        raise ServiceOperationError('Erro ao deletar') from error
