from datetime import datetime
import hashlib
import hmac

from werkzeug.security import check_password_hash, generate_password_hash

from src.database import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        stored_hash = self.password or ''
        if len(stored_hash) == 32:
            try:
                int(stored_hash, 16)
            except ValueError:
                return False
            if hmac.compare_digest(stored_hash, hashlib.md5(pwd.encode()).hexdigest()):
                self.set_password(pwd)
                return True
            return False
        try:
            return check_password_hash(stored_hash, pwd)
        except (ValueError, TypeError):
            return False

    def is_admin(self):
        return self.role == 'admin'
