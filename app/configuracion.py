"""Configuración de la aplicación."""
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Variables de configuración."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'sgpt-dev-secret-key-2026')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(basedir, "instance", "sgpt.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    NOTIFICATIONS_MAX_PER_DAY = 5