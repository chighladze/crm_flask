from flask import Blueprint, abort, request, render_template, redirect, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user
from ..extensions import db, bcrypt
from ..forms.users import UserCreateForm, LoginForm
from ..models.users import Users
from datetime import datetime

users = Blueprint('users', __name__)


@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.passwordHash, form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Вы успешно авторизованы", "success")
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        else:
            flash("Ошибка авторизации. Проверьте email и пароль.", "danger")
    return render_template('main/login.html', form=form)


@users.route('/users/create', methods=['GET', 'POST'])
@login_required
def user_create():
    form = UserCreateForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user = Users(
            name=form.name.data,
            email=form.email.data,
            passwordHash=hashed_password,
            createdAt=datetime.utcnow(),
            updatedAt=datetime.utcnow()
        )

        db.session.add(user)
        db.session.commit()

        flash('Пользователь успешно создан!', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('users/create.html', form=form)


@users.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('users.login'))
