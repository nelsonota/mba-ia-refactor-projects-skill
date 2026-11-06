from src.services.auth_service import AuthService


class AuthController:
    """Coordinates the login use case without accessing persistence directly."""

    @staticmethod
    def authenticate(email, password):
        return AuthService.authenticate(email, password)
