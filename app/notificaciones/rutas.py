"""Historial de notificaciones y lectura."""
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.notificaciones import notifications_bp
from app.modelos import Notification
from app.configuracion import Config


@notifications_bp.route('/')
@login_required
def listar():
    """Lista de notificaciones."""
    notificaciones = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    sin_leer = Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).count()

    return render_template(
        'notificaciones/lista.html',
        notificaciones=notificaciones,
        sin_leer=sin_leer
    )


@notifications_bp.route('/leer/<int:notif_id>')
@login_required
def marcar_leida(notif_id: int):
    """Marca una como leída."""
    notif = Notification.query.filter_by(
        id=notif_id, user_id=current_user.id
    ).first_or_404()
    notif.is_read = True
    db.session.commit()
    return redirect(url_for('notificaciones.listar'))


@notifications_bp.route('/leer-todas')
@login_required
def marcar_todas_leidas():
    """Marca todas como leídas."""
    Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).update({'is_read': True})
    db.session.commit()
    flash('Todas marcadas como leídas.', 'info')
    return redirect(url_for('notificaciones.listar'))


def check_and_generate_notifications() -> None:
    """
    Crea notificaciones para tareas vencidas.
    Reglas: 48h de vencimiento, max 5 por día, sin duplicados.
    Se llama desde un scheduler.
    """
    from datetime import datetime, timezone, timedelta
    from app.modelos import Task, Status

    ahora = datetime.now(timezone.utc)
    activo = Status.query.filter_by(name='activo').first()
    pausa = Status.query.filter_by(name='en pausa').first()

    if not activo and not pausa:
        return

    ids_estados = [s.id for s in [activo, pausa] if s]

    hace_48h = ahora - timedelta(hours=48)
    inicio_hoy = ahora.replace(hour=0, minute=0, second=0, microsecond=0)

    tareas_vencidas = Task.query.filter(
        Task.due_date <= hace_48h,
        Task.status_id.in_(ids_estados)
    ).all()

    for tarea in tareas_vencidas:
        usuario = tarea.assignee
        if not usuario:
            continue

        recientes = Notification.query.filter(
            Notification.user_id == usuario.id,
            Notification.created_at >= inicio_hoy
        ).count()

        if recientes >= Config.NOTIFICATIONS_MAX_PER_DAY:
            continue

        ya_notificada = Notification.query.filter(
            Notification.user_id == usuario.id,
            Notification.task_id == tarea.id,
            Notification.created_at >= inicio_hoy
        ).first()

        if ya_notificada:
            continue

        mensaje = f'Tarea vencida: "{tarea.title}" en "{tarea.project.name}"'
        notif = Notification(user_id=usuario.id, task_id=tarea.id, message=mensaje)
        db.session.add(notif)

    db.session.commit()