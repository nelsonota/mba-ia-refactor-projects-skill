from src.models.constants import ROLE_ADMIN
from functools import wraps
from flask import current_app, jsonify, request, g
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

TOKEN_SALT = 'task-manager-auth-v1'


def issue_token(user_id, role):
    secret = current_app.config.get('SECRET_KEY')
    if not secret:
        return None
    serializer = URLSafeTimedSerializer(secret, salt=TOKEN_SALT)
    return serializer.dumps({'user_id': user_id, 'role': role})


def require_admin():
    secret = current_app.config.get('SECRET_KEY')
    if not secret:
        return jsonify({'error': 'Autenticação indisponível'}), 503
    header = request.headers.get('Authorization', '')
    scheme, _, token = header.partition(' ')
    if scheme.lower() != 'bearer' or not token:
        return jsonify({'error': 'Autenticação obrigatória'}), 401
    serializer = URLSafeTimedSerializer(secret, salt=TOKEN_SALT)
    try:
        identity = serializer.loads(token, max_age=current_app.config['TOKEN_MAX_AGE_SECONDS'])
    except (BadSignature, SignatureExpired):
        return jsonify({'error': 'Credencial inválida'}), 401
    if identity.get('role') != ROLE_ADMIN:
        return jsonify({'error': 'Acesso negado'}), 403
    g.identity = identity
    return None


def admin_blueprint_guard(blueprint, public_endpoints=()):
    @blueprint.before_request
    def authorize_request():
        if request.endpoint in public_endpoints:
            return None
        return require_admin()



