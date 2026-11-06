import os

class Settings:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///tasks.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('TASK_MANAGER_SECRET_KEY')
    TOKEN_MAX_AGE_SECONDS = int(os.getenv('TOKEN_MAX_AGE_SECONDS', '3600'))
    DEBUG = os.getenv('FLASK_DEBUG', '').lower() == 'true'
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
