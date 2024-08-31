from flask import Blueprint, abort, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user, logout_user, login_user
from ..extensions import db, bcrypt
from ..forms.users import UserCreateForm, LoginForm
from ..models.users import Users
from datetime import datetime

users = Blueprint('users', __name__)


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

        flash('მონაცემები შენახული!', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('users/create.html', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():  # POST method check is not needed here
        user = Users.query.filter_by(email=form.email.data).first()  # Use 'email' instead of 'login'
        if user and bcrypt.check_password_hash(user.passwordHash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash("Вы успешно авторизованы", "success")
            return redirect(next_page) if next_page else redirect(url_for('dashboard.index'))
        else:
            flash("ავტორიზაციის შეცდომა. გადაამოწმეთ მეილი და პაროლი.", "danger")
    return render_template('main/login.html', form=form)


@users.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('users.login'))

