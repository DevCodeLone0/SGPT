"""Módulo de proyectos: listado, detalle, creación, edición y eliminación."""
from flask import Blueprint

projects_bp = Blueprint('proyectos', __name__, url_prefix='/proyectos')