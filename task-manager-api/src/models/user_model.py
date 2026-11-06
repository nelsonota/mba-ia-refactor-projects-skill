from src.models.constants import DEFAULT_USER_ROLE, ROLE_ADMIN
from src.services.clock import utc_now
from database import db
import hashlib
import hmac
from werkzeug.security import check_password_hash, generate_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default=DEFAULT_USER_ROLE)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at)
        }

    def set_password(self, pwd):

        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        stored_hash = self.password or ''
        if len(stored_hash) == 32:
            legacy_hash = hashlib.md5(pwd.encode()).hexdigest()
            if not hmac.compare_digest(stored_hash, legacy_hash):
                return False
            self.set_password(pwd)
            return True
        try:
            return check_password_hash(stored_hash, pwd)
        except (ValueError, TypeError):
            return False

    def is_admin(self):
        if self.role == ROLE_ADMIN:
            return True
        else:
            return False

