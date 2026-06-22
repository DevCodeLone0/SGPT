"""Login, registro y logout."""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.autenticacion import auth_bp
from app.modelos import User


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Formulario de inicio de sesión."""
    if current_user.is_authenticated:
        return redirect(url_for('inicio.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            flash(f'¡Bienvenido de vuelta, {user.name}!', 'success')
            return redirect(request.args.get('next') or url_for('inicio.index'))

        flash('El correo o la contraseña no son correctos.', 'error')

    return render_template('autenticacion/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Formulario para crear cuenta nueva."""
    if current_user.is_authenticated:
        return redirect(url_for('inicio.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        errores = []
        if len(name) < 2 or len(name) > 100:
            errores.append('El nombre tiene que tener entre 2 y 100 caracteres.')
        if not email or '@' not in email:
            errores.append('Poné un correo válido.')
        if len(password) < 6:
            errores.append('La contraseña debe tener al menos 6 caracteres.')
        if User.query.filter_by(email=email).first():
            errores.append('Ese correo ya está registrado.')

        if errores:
            for e in errores:
                flash(e, 'error')
            return render_template('autenticacion/register.html')

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('¡Cuenta creada! Bienvenido.', 'success')
        login_user(user, remember=True)
        return redirect(url_for('inicio.index'))

    return render_template('autenticacion/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Cierra la sesión."""
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('autenticacion.login'))