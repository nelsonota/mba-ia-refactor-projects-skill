from src.services.clock import utc_now
"""Script para popular o banco com dados iniciais"""
from app import app, db
from models.task import Task
from models.user import User
from models.category import Category
from src.models.constants import STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_DONE, STATUS_CANCELLED, PRIORITY_CRITICAL, PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_LOW, PRIORITY_MINIMAL, DEFAULT_USER_ROLE, ROLE_ADMIN, ROLE_MANAGER
from datetime import datetime, timedelta

def seed_data():
    with app.app_context():

        Task.query.delete()
        User.query.delete()
        Category.query.delete()
        db.session.commit()

        admin_user = User()
        admin_user.name = 'JoÃ£o Silva'
        admin_user.email = 'joao@email.com'
        admin_user.set_password('1234')
        admin_user.role = ROLE_ADMIN
        db.session.add(admin_user)

        regular_user = User()
        regular_user.name = 'Maria Santos'
        regular_user.email = 'maria@email.com'
        regular_user.set_password('abcd')
        regular_user.role = DEFAULT_USER_ROLE
        db.session.add(regular_user)

        manager_user = User()
        manager_user.name = 'Pedro Oliveira'
        manager_user.email = 'pedro@email.com'
        manager_user.set_password('pass')
        manager_user.role = ROLE_MANAGER
        db.session.add(manager_user)

        db.session.commit()

        backend_category = Category()
        backend_category.name = 'Backend'
        backend_category.description = 'Tarefas de backend'
        backend_category.color = '#3498db'
        db.session.add(backend_category)

        frontend_category = Category()
        frontend_category.name = 'Frontend'
        frontend_category.description = 'Tarefas de frontend'
        frontend_category.color = '#2ecc71'
        db.session.add(frontend_category)

        devops_category = Category()
        devops_category.name = 'DevOps'
        devops_category.description = 'Tarefas de infraestrutura'
        devops_category.color = '#e74c3c'
        db.session.add(devops_category)

        bug_category = Category()
        bug_category.name = 'Bug'
        bug_category.description = 'CorreÃ§Ã£o de bugs'
        bug_category.color = '#e67e22'
        db.session.add(bug_category)

        db.session.commit()

        tasks_data = [
            {'title': 'Implementar autenticaÃ§Ã£o JWT', 'description': 'Adicionar autenticaÃ§Ã£o real com JWT', 'status': STATUS_PENDING, 'priority': PRIORITY_CRITICAL, 'user_id': admin_user.id, 'category_id': backend_category.id, 'due_date': utc_now() - timedelta(days=3)},
            {'title': 'Criar tela de login', 'description': 'Tela de login responsiva', 'status': STATUS_IN_PROGRESS, 'priority': PRIORITY_HIGH, 'user_id': regular_user.id, 'category_id': frontend_category.id, 'due_date': utc_now() + timedelta(days=5)},
            {'title': 'Configurar CI/CD', 'description': 'Pipeline com GitHub Actions', 'status': STATUS_DONE, 'priority': PRIORITY_HIGH, 'user_id': manager_user.id, 'category_id': devops_category.id, 'tags': 'devops,ci,github'},
            {'title': 'Corrigir bug no filtro de busca', 'description': 'Filtro nÃ£o funciona com caracteres especiais', 'status': STATUS_PENDING, 'priority': PRIORITY_CRITICAL, 'user_id': admin_user.id, 'category_id': bug_category.id, 'due_date': utc_now() - timedelta(days=1)},
            {'title': 'Adicionar paginaÃ§Ã£o na API', 'description': 'Endpoints retornam todos os registros', 'status': STATUS_PENDING, 'priority': PRIORITY_MEDIUM, 'user_id': admin_user.id, 'category_id': backend_category.id, 'due_date': utc_now() + timedelta(days=10)},
            {'title': 'Escrever testes unitÃ¡rios', 'description': 'Cobertura mÃ­nima de 80%', 'status': STATUS_PENDING, 'priority': PRIORITY_HIGH, 'user_id': regular_user.id, 'category_id': backend_category.id},
            {'title': 'Documentar API com Swagger', 'description': 'Gerar documentaÃ§Ã£o automÃ¡tica', 'status': STATUS_CANCELLED, 'priority': PRIORITY_LOW, 'user_id': manager_user.id, 'category_id': backend_category.id},
            {'title': 'Refatorar models', 'description': 'Melhorar organizaÃ§Ã£o dos models', 'status': STATUS_IN_PROGRESS, 'priority': PRIORITY_MEDIUM, 'user_id': regular_user.id, 'category_id': backend_category.id, 'tags': 'refactor,tech-debt'},
            {'title': 'Configurar monitoramento', 'description': 'Prometheus + Grafana', 'status': STATUS_PENDING, 'priority': PRIORITY_LOW, 'user_id': manager_user.id, 'category_id': devops_category.id, 'due_date': utc_now() + timedelta(days=20)},
            {'title': 'Melhorar validaÃ§Ãµes de input', 'description': 'Usar marshmallow ou pydantic', 'status': STATUS_PENDING, 'priority': PRIORITY_MEDIUM, 'user_id': admin_user.id, 'category_id': backend_category.id, 'tags': 'improvement,validation'},
        ]

        for task_data in tasks_data:
            task = Task()
            task.title = task_data['title']
            task.description = task_data['description']
            task.status = task_data['status']
            task.priority = task_data['priority']
            task.user_id = task_data['user_id']
            task.category_id = task_data['category_id']
            if 'due_date' in task_data:
                task.due_date = task_data['due_date']
            if 'tags' in task_data:
                task.tags = task_data['tags']
            db.session.add(task)

        db.session.commit()
        print("Seed concluÃ­do com sucesso!")
        print(f"  {User.query.count()} usuÃ¡rios")
        print(f"  {Category.query.count()} categorias")
        print(f"  {Task.query.count()} tasks")

if __name__ == '__main__':
    seed_data()
