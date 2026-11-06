from src.services.clock import utc_now
from src.models.constants import VALID_TASK_STATUSES, MIN_TASK_PRIORITY, MAX_TASK_PRIORITY, DEFAULT_TASK_PRIORITY, MAX_TASK_TITLE_LENGTH, STATUS_PENDING, STATUS_DONE, STATUS_CANCELLED
from database import db

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(MAX_TASK_TITLE_LENGTH), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default=STATUS_PENDING)
    priority = db.Column(db.Integer, default=DEFAULT_TASK_PRIORITY)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)
    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')

    def to_dict(self):
        return {'id': self.id, 'title': self.title, 'description': self.description, 'status': self.status,
                'priority': self.priority, 'user_id': self.user_id, 'category_id': self.category_id,
                'created_at': str(self.created_at), 'updated_at': str(self.updated_at),
                'due_date': str(self.due_date) if self.due_date else None,
                'tags': self.tags.split(',') if self.tags else []}

    def validate_status(self, new_status):
        return new_status in VALID_TASK_STATUSES

    def validate_priority(self, priority):
        return MIN_TASK_PRIORITY <= priority <= MAX_TASK_PRIORITY

    def is_overdue(self):
        return bool(self.due_date and self.due_date < utc_now() and self.status not in (STATUS_DONE, STATUS_CANCELLED, STATUS_PENDING, DEFAULT_TASK_PRIORITY))






