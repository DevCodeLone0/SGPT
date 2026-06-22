"""Listar, crear, ver, editar y borrar proyectos."""
from datetime import datetime, timezone
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.proyectos import projects_bp
from app.modelos import Project, Status, Priority, Task


@projects_bp.route('/')
@login_required
def listar():
    """Lista de proyectos con filtros."""
    estado_filtro = request.args.get('status', type=int)
    prioridad_filtro = request.args.get('priority', type=int)

    query = Project.query.filter_by(user_id=current_user.id)

    if estado_filtro:
        query = query.filter_by(status_id=estado_filtro)
    if prioridad_filtro:
        query = query.filter_by(priority_id=prioridad_filtro)

    proyectos = query.order_by(Project.updated_at.desc()).all()
    estados = Status.query.all()
    prioridades = Priority.query.all()

    return render_template(
        'proyectos/lista.html',
        proyectos=proyectos,
        estados=estados,
        prioridades=prioridades,
        estado_actual=estado_filtro,
        prioridad_actual=prioridad_filtro
    )


@projects_bp.route('/<int:project_id>')
@login_required
def detalle(project_id: int):
    """Detalle del proyecto con Kanban de tareas."""
    proyecto = Project.query.filter_by(
        id=project_id, user_id=current_user.id
    ).first_or_404()
    tareas = Task.query.filter_by(
        project_id=proyecto.id
    ).order_by(Task.due_date.asc()).all()
    estados = Status.query.all()
    prioridades = Priority.query.all()

    por_estado = {s.name: [] for s in estados}
    for tarea in tareas:
        por_estado[tarea.status.name].append(tarea)

    return render_template(
        'proyectos/detalle.html',
        proyecto=proyecto,
        tareas=tareas,
        por_estado=por_estado,
        estados=estados,
        prioridades=prioridades
    )


@projects_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    """Crear proyecto nuevo."""
    estados = Status.query.all()
    prioridades = Priority.query.all()

    if request.method == 'POST':
        nombre = request.form.get('name', '').strip()
        descripcion = request.form.get('description', '').strip()
        fecha_limite = request.form.get('due_date', '')
        estado_id = request.form.get('status_id', type=int)
        prioridad_id = request.form.get('priority_id', type=int)

        errores = []
        if not nombre or len(nombre) < 3 or len(nombre) > 100:
            errores.append('El nombre debe tener entre 3 y 100 caracteres.')
        if not estado_id:
            errores.append('Elegí un estado.')
        if not prioridad_id:
            errores.append('Elegí una prioridad.')

        fecha = None
        if fecha_limite:
            try:
                fecha = datetime.fromisoformat(fecha_limite).replace(tzinfo=timezone.utc)
            except ValueError:
                errores.append('La fecha límite no es válida.')

        if errores:
            for e in errores:
                flash(e, 'error')
            return render_template(
                'proyectos/formulario.html',
                estados=estados, prioridades=prioridades,
                proyecto=None, es_edicion=False
            )

        proyecto = Project(
            name=nombre,
            description=descripcion,
            due_date=fecha,
            status_id=estado_id,
            priority_id=prioridad_id,
            user_id=current_user.id
        )
        db.session.add(proyecto)
        db.session.commit()
        flash('Proyecto creado.', 'success')
        return redirect(url_for('proyectos.detalle', project_id=proyecto.id))

    return render_template(
        'proyectos/formulario.html',
        estados=estados, prioridades=prioridades,
        proyecto=None, es_edicion=False
    )


@projects_bp.route('/<int:project_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(project_id: int):
    """Editar proyecto existente."""
    proyecto = Project.query.filter_by(
        id=project_id, user_id=current_user.id
    ).first_or_404()
    estados = Status.query.all()
    prioridades = Priority.query.all()

    if request.method == 'POST':
        nombre = request.form.get('name', '').strip()
        descripcion = request.form.get('description', '').strip()
        fecha_limite = request.form.get('due_date', '')
        estado_id = request.form.get('status_id', type=int)
        prioridad_id = request.form.get('priority_id', type=int)

        errores = []
        if not nombre or len(nombre) < 3 or len(nombre) > 100:
            errores.append('El nombre debe tener entre 3 y 100 caracteres.')
        if not estado_id:
            errores.append('Elegí un estado.')
        if not prioridad_id:
            errores.append('Elegí una prioridad.')

        if fecha_limite:
            try:
                proyecto.due_date = datetime.fromisoformat(fecha_limite).replace(tzinfo=timezone.utc)
            except ValueError:
                errores.append('La fecha límite no es válida.')
        else:
            proyecto.due_date = None

        if errores:
            for e in errores:
                flash(e, 'error')
            return render_template(
                'proyectos/formulario.html',
                proyecto=proyecto, estados=estados,
                prioridades=prioridades, es_edicion=True
            )

        proyecto.name = nombre
        proyecto.description = descripcion
        proyecto.status_id = estado_id
        proyecto.priority_id = prioridad_id
        db.session.commit()
        flash('Proyecto actualizado.', 'success')
        return redirect(url_for('proyectos.detalle', project_id=proyecto.id))

    return render_template(
        'proyectos/formulario.html',
        proyecto=proyecto, estados=estados,
        prioridades=prioridades, es_edicion=True
    )


@projects_bp.route('/<int:project_id>/eliminar', methods=['POST'])
@login_required
def eliminar(project_id: int):
    """Borra el proyecto y todas sus tareas."""
    proyecto = Project.query.filter_by(
        id=project_id, user_id=current_user.id
    ).first_or_404()
    db.session.delete(proyecto)
    db.session.commit()
    flash(f'"{proyecto.name}" y sus tareas fueron eliminados.', 'info')
    return redirect(url_for('proyectos.listar'))