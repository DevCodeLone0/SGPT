"""Crear, editar, completar y borrar tareas."""
from datetime import datetime, timezone
from flask import redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.tareas import tasks_bp
from app.modelos import Task, Project, Status, Priority


@tasks_bp.route('/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle(task_id: int):
    """Completa o descomplecta una tarea con un click."""
    tarea = Task.query.filter_by(
        id=task_id, user_id=current_user.id
    ).first_or_404()
    completado = Status.query.filter_by(name='completado').first()
    activo = Status.query.filter_by(name='activo').first()

    if tarea.status.name == 'completado':
        tarea.status_id = activo.id
    else:
        tarea.status_id = completado.id

    db.session.commit()
    return jsonify({'status': 'ok', 'nuevo_estado': tarea.status.name})


@tasks_bp.route('/<int:task_id>/cambiar-estado', methods=['POST'])
@login_required
def cambiar_estado(task_id: int):
    """Cambia el estado desde el dropdown."""
    tarea = Task.query.filter_by(
        id=task_id, user_id=current_user.id
    ).first_or_404()
    nuevo = db.session.get(Status, request.form.get('status_id', type=int))
    if nuevo:
        tarea.status_id = nuevo.id
        db.session.commit()
    return redirect(url_for('proyectos.detalle', project_id=tarea.project_id))


@tasks_bp.route('/crear/<int:project_id>', methods=['POST'])
@login_required
def crear(project_id: int):
    """Crear tarea dentro de un proyecto."""
    proyecto = Project.query.filter_by(
        id=project_id, user_id=current_user.id
    ).first_or_404()

    titulo = request.form.get('title', '').strip()
    descripcion = request.form.get('description', '').strip()
    vencimiento = request.form.get('due_date', '')
    estado_id = request.form.get('status_id', type=int)
    prioridad_id = request.form.get('priority_id', type=int)

    errores = []
    if not titulo:
        errores.append('El título es obligatorio.')
    elif len(titulo) > 100:
        errores.append('El título no puede pasar de 100 caracteres.')
    if not vencimiento:
        errores.append('La fecha de vencimiento es obligatoria.')
    if not estado_id:
        errores.append('Elegí un estado.')
    if not prioridad_id:
        errores.append('Elegí una prioridad.')

    fecha = None
    if vencimiento:
        try:
            fecha = datetime.fromisoformat(vencimiento).replace(tzinfo=timezone.utc)
        except ValueError:
            errores.append('La fecha no es válida.')

    if errores:
        for e in errores:
            flash(e, 'error')
        return redirect(url_for('proyectos.detalle', project_id=project_id))

    tarea = Task(
        title=titulo,
        description=descripcion,
        due_date=fecha,
        status_id=estado_id,
        priority_id=prioridad_id,
        project_id=project_id,
        user_id=current_user.id
    )
    db.session.add(tarea)
    db.session.commit()
    flash('Tarea creada.', 'success')
    return redirect(url_for('proyectos.detalle', project_id=project_id))


@tasks_bp.route('/<int:task_id>/editar', methods=['POST'])
@login_required
def editar(task_id: int):
    """Editar una tarea."""
    tarea = Task.query.filter_by(
        id=task_id, user_id=current_user.id
    ).first_or_404()

    titulo = request.form.get('title', '').strip()
    descripcion = request.form.get('description', '').strip()
    vencimiento = request.form.get('due_date', '')
    estado_id = request.form.get('status_id', type=int)
    prioridad_id = request.form.get('priority_id', type=int)

    errores = []
    if not titulo:
        errores.append('El título es obligatorio.')
    elif len(titulo) > 100:
        errores.append('El título no puede pasar de 100 caracteres.')
    if not vencimiento:
        errores.append('La fecha de vencimiento es obligatoria.')
    if not estado_id:
        errores.append('Elegí un estado.')
    if not prioridad_id:
        errores.append('Elegí una prioridad.')

    if vencimiento:
        try:
            tarea.due_date = datetime.fromisoformat(vencimiento).replace(tzinfo=timezone.utc)
        except ValueError:
            errores.append('La fecha no es válida.')

    if errores:
        for e in errores:
            flash(e, 'error')
        return redirect(url_for('proyectos.detalle', project_id=tarea.project_id))

    tarea.title = titulo
    tarea.description = descripcion
    tarea.status_id = estado_id
    tarea.priority_id = prioridad_id
    db.session.commit()

    flash('Tarea actualizada.', 'success')
    return redirect(url_for('proyectos.detalle', project_id=tarea.project_id))


@tasks_bp.route('/<int:task_id>/eliminar', methods=['POST'])
@login_required
def eliminar(task_id: int):
    """Borra una tarea."""
    tarea = Task.query.filter_by(
        id=task_id, user_id=current_user.id
    ).first_or_404()
    project_id = tarea.project_id
    db.session.delete(tarea)
    db.session.commit()
    flash('Tarea eliminada.', 'info')
    return redirect(url_for('proyectos.detalle', project_id=project_id))