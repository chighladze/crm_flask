from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_login import login_user, login_required, current_user, logout_user
import sqlalchemy as sa
from ..extensions import db, bcrypt
from ..forms.users import UserCreateForm, LoginForm
from ..models.users import Users
from datetime import datetime
from urllib.parse import urlparse, urljoin

users = Blueprint('users', __name__)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(Users).where(Users.email == form.email.data))

        if user is None or not bcrypt.check_password_hash(user.passwordHash, form.password.data):
            flash('მონაცემები არ არის სწორი')
            return redirect(url_for('users.login'))

        login_user(user, remember=form.remember.data)
        return redirect(request.args.get('next') or url_for('dashboard.index'))

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
        flash('ახალი მომხმარებელი წარმატებით შექმნილია!', 'success')
        return redirect(url_for('dashboard.index'))
    return render_template('users/create.html', form=form)


@users.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    user_id = current_user.get_id()
    session.pop(user_id, None)
    logout_user()
    return redirect(url_for('users.login'))
