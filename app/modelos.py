"""Los modelos de la base de datos."""
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class Status(db.Model):
    """Lo mismo para todos: activo, en pausa, completado."""
    __tablename__ = 'statuses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Status {self.name}>'


class Priority(db.Model):
    """Alta, media o baja."""
    __tablename__ = 'priorities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Priority {self.name}>'

class numerodeTareas(db.Model):
    """Modelo para filtrar proyectos por número de tareas."""
    __tablename__ = 'numerodetareas'
    id = db.Column(db.Integer, primary_key=True)
    range = db.Column(db.String(20), unique=True, nullable=False)

    def __repr__(self):
        return f'<NumerodeTareas {self.range}>'

class User(UserMixin, db.Model):
    """Un usuario registrado."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    projects = db.relationship('Project', back_populates='owner', lazy='dynamic')
    tasks = db.relationship('Task', back_populates='assignee', lazy='dynamic')
    notifications = db.relationship('Notification', back_populates='user', lazy='dynamic')

    def set_password(self, password: str) -> None:
        """Guarda la contraseña hasheada."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Checkea si la contraseña está bien."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'


class Project(db.Model):
    """Un proyecto, pertenece a un usuario."""
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    start_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    due_date = db.Column(db.DateTime, nullable=True)
    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'), nullable=False)
    priority_id = db.Column(db.Integer, db.ForeignKey('priorities.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    owner = db.relationship('User', back_populates='projects')
    status = db.relationship('Status')
    priority = db.relationship('Priority')
    tasks = db.relationship('Task', back_populates='project', lazy='dynamic',
                             cascade='all, delete-orphan')

    @property
    def task_count(self) -> int:
        """Cuántas tareas tiene."""
        return self.tasks.count()

    @property
    def completed_tasks(self) -> int:
        """Cuántas están completadas."""
        completado = Status.query.filter_by(name='completado').first()
        if completado:
            return self.tasks.filter_by(status_id=completado.id).count()
        return 0

    @property
    def progress_percent(self) -> int:
        """Porcentaje de progreso."""
        total = self.task_count
        if total == 0:
            return 0
        return int((self.completed_tasks / total) * 100)

    def __repr__(self):
        return f'<Project {self.name}>'


class Task(db.Model):
    """Una tarea, dentro de un proyecto."""
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    due_date = db.Column(db.DateTime, nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id'), nullable=False)
    priority_id = db.Column(db.Integer, db.ForeignKey('priorities.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    project = db.relationship('Project', back_populates='tasks')
    assignee = db.relationship('User', back_populates='tasks')
    status = db.relationship('Status')
    priority = db.relationship('Priority')
    notifications = db.relationship('Notification', back_populates='task',
                                    cascade='all, delete-orphan')

    @property
    def is_overdue(self) -> bool:
        """Si ya venció y no está completada."""
        if self.due_date:
            ahora = datetime.now(timezone.utc) if self.due_date.tzinfo else datetime.now()
            return self.due_date < ahora
        return False

    def __repr__(self):
        return f'<Task {self.title}>'


class Notification(db.Model):
    """Una notificación para el usuario."""
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)
    message = db.Column(db.String(300), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', back_populates='notifications')
    task = db.relationship('Task', back_populates='notifications')

    def __repr__(self):
        return f'<Notification #{self.id}>'