"""Módulo de autenticación: login, registro y cierre de sesión."""
from flask import Blueprint

auth_bp = Blueprint('autenticacion', __name__, url_prefix='/auth')