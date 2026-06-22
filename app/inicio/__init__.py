"""Módulo de inicio (dashboard): página principal con métricas."""
from flask import Blueprint

dashboard_bp = Blueprint('inicio', __name__, url_prefix='/inicio')