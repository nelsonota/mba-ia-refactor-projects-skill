import smtplib
from datetime import datetime
from src.config.settings import Settings

class NotificationService:
    def __init__(self):
        self.notifications = []
        self.email_host = Settings.SMTP_HOST
        self.email_port = Settings.SMTP_PORT
        self.email_user = Settings.SMTP_USER
        self.email_password = Settings.SMTP_PASSWORD

    def send_email(self, to, subject, body):
        if not self.email_user or not self.email_password:
            return False
        try:
            with smtplib.SMTP(self.email_host, self.email_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.sendmail(self.email_user, to, f"Subject: {subject}\n\n{body}")
            return True
        except (OSError, smtplib.SMTPException):
            return False

    def notify_task_assigned(self, user, task):
        self.send_email(user.email, f"Nova task atribuída: {task.title}",
                        f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\nPrioridade: {task.priority}\nStatus: {task.status}")
        self.notifications.append({'type': 'task_assigned', 'user_id': user.id,
                                   'task_id': task.id, 'timestamp': datetime.now()})

    def notify_task_overdue(self, user, task):
        self.send_email(user.email, f"Task atrasada: {task.title}",
                        f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\nData limite: {task.due_date}")

    def get_notifications(self, user_id):
        return [notification for notification in self.notifications if notification['user_id'] == user_id]
