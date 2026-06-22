"""Módulo de tareas: creación, edición, completado y eliminación."""
from flask import Blueprint

tasks_bp = Blueprint('tareas', __name__, url_prefix='/tareas')