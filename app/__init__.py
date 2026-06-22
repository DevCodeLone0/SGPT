"""La fábrica de la aplicación."""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.configuracion import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'autenticacion.login'
login_manager.login_message = 'Necesitás iniciar sesión para entrar.'
login_manager.login_message_category = 'info'


def create_app(config_class=Config) -> Flask:
    """Acá se arma todo."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    instance_path = os.path.join(app.root_path, 'instance')
    os.makedirs(instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from app.autenticacion.rutas import auth_bp
    from app.proyectos.rutas import projects_bp
    from app.tareas.rutas import tasks_bp
    from app.inicio.rutas import dashboard_bp, root_bp
    from app.notificaciones.rutas import notifications_bp

    app.register_blueprint(root_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(notifications_bp)

    with app.app_context():
        from app.modelos import User, Status, Priority  # noqa: F401
        db.create_all()
        _seed_defaults()

    @app.context_processor
    def inject_globals():
        from datetime import datetime, timezone
        from flask_login import current_user
        if current_user.is_authenticated:
            from app.modelos import Notification
            unread = Notification.query.filter_by(
                user_id=current_user.id, is_read=False
            ).count()
        else:
            unread = 0
        return dict(unread_notif_count=unread, current_dt=datetime.now(timezone.utc))

    return app


@login_manager.user_loader
def load_user(user_id: int):
    """Carga el usuario por ID."""
    from app.modelos import User
    return db.session.get(User, int(user_id))


def _seed_defaults() -> None:
    """Crea los estados y prioridades base."""
    from app.modelos import Status, Priority

    for name in ['activo', 'en pausa', 'completado']:
        if not Status.query.filter_by(name=name).first():
            db.session.add(Status(name=name))

    for name in ['alta', 'media', 'baja']:
        if not Priority.query.filter_by(name=name).first():
            db.session.add(Priority(name=name))

    db.session.commit()