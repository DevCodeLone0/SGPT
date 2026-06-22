"""Dashboard (página principal) y raíz."""
from datetime import datetime, timezone, timedelta
from flask import render_template, Blueprint, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.inicio import dashboard_bp
from app.modelos import Project, Task, Status, Notification


@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard con métricas rápidas."""
    proyectos = Project.query.filter_by(user_id=current_user.id).all()
    total_proyectos = len(proyectos)
    total_tareas = Task.query.filter_by(user_id=current_user.id).count()

    completado = Status.query.filter_by(name='completado').first()
    tareas_completadas = (
        Task.query.filter_by(
            user_id=current_user.id, status_id=completado.id
        ).count() if completado else 0
    )

    activo = Status.query.filter_by(name='activo').first()
    pausa = Status.query.filter_by(name='en pausa').first()
    estados_activos = [activo.id, pausa.id] if activo and pausa else []

    ahora = datetime.now(timezone.utc)
    vencidas = Task.query.filter(
        Task.user_id == current_user.id,
        Task.due_date < ahora,
        Task.status_id.in_(estados_activos)
    ).count() if estados_activos else 0

    notificaciones_no_leidas = Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).count()

    proyectos_recientes = (
        Project.query.filter_by(user_id=current_user.id)
        .order_by(Project.updated_at.desc())
        .limit(5)
        .all()
    )

    en_siete_dias = ahora + timedelta(days=7)
    tareas_proximas = Task.query.filter(
        Task.user_id == current_user.id,
        Task.due_date.between(ahora, en_siete_dias),
        Task.status_id.in_(estados_activos)
    ).order_by(Task.due_date.asc()).limit(10).all() if estados_activos else []

    return render_template(
        'inicio/index.html',
        total_proyectos=total_proyectos,
        total_tareas=total_tareas,
        tareas_completadas=tareas_completadas,
        tareas_vencidas=vencidas,
        notificaciones_no_leidas=notificaciones_no_leidas,
        proyectos_recientes=proyectos_recientes,
        tareas_proximas=tareas_proximas
    )


root_bp = Blueprint('root', __name__)


@root_bp.route('/')
def root():
    """Raíz: redirige a dashboard o login."""
    if current_user.is_authenticated:
        return redirect(url_for('inicio.index'))
    return redirect(url_for('autenticacion.login'))