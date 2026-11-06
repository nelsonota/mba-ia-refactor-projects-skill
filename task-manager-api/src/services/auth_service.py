from database import db
from models.user import User
from src.middlewares.auth import issue_token


class AuthService:
    """Owns credential lookup, password migration, and token issuance."""

    @staticmethod
    def authenticate(email, password):
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return None, 'invalid'
        if not user.active:
            return None, 'inactive'
        token = issue_token(user.id, user.role)
        if token is None:
            return None, 'unavailable'
        db.session.commit()
        return {
            'message': 'Login realizado com sucesso',
            'user': user.to_dict(),
            'token': token,
        }, None
