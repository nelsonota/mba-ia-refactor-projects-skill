from src.services import user_service
from src.controllers.auth_controller import AuthController


class UserController:
    @staticmethod
    def get_users(data=None, query_args=None):
        return user_service.get_users(data=data, query_args=query_args)

    @staticmethod
    def get_user(user_id=None, data=None, query_args=None):
        return user_service.get_user(user_id=user_id, data=data, query_args=query_args)

    @staticmethod
    def create_user(data=None, query_args=None):
        return user_service.create_user(data=data, query_args=query_args)

    @staticmethod
    def update_user(user_id=None, data=None, query_args=None):
        return user_service.update_user(user_id=user_id, data=data, query_args=query_args)

    @staticmethod
    def delete_user(user_id=None, data=None, query_args=None):
        return user_service.delete_user(user_id=user_id, data=data, query_args=query_args)

    @staticmethod
    def get_user_tasks(user_id=None, data=None, query_args=None):
        return user_service.get_user_tasks(user_id=user_id, data=data, query_args=query_args)

    @staticmethod
    def login(data=None):
        if not data:
            return {'error': 'Dados inv\u00e1lidos'}, 400
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return {'error': 'Email e senha s\u00e3o obrigat\u00f3rios'}, 400
        response, error = AuthController.authenticate(email, password)
        if error == 'invalid':
            return {'error': 'Credenciais inv\u00e1lidas'}, 401
        if error == 'inactive':
            return {'error': 'Usu\u00e1rio inativo'}, 403
        if error == 'unavailable':
            return {'error': 'Autentica\u00e7\u00e3o indispon\u00edvel'}, 503
        return response, 200
