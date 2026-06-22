"""Módulo de notificaciones: historial y marcado de lectura."""
from flask import Blueprint

notifications_bp = Blueprint('notificaciones', __name__, url_prefix='/notificaciones')