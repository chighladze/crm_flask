from flask import Blueprint, request, render_template, redirect, url_for, flash, session, send_file
from flask_login import login_user, login_required, current_user, logout_user
import sqlalchemy as sa
from ..extensions import db, bcrypt
from ..forms.users import UserCreateForm, LoginForm
from ..models.users import Users
from datetime import datetime
from urllib.parse import urlparse, urljoin
import pandas as pd
from io import BytesIO

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

        user.lastLogin = datetime.utcnow()
        db.session.commit()

        return redirect(request.args.get('next') or url_for('dashboard.index'))

    return render_template('main/login.html', form=form)


@users.route('/users/user_list', methods=['GET', 'POST'])
@login_required
def users_list():
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)  # Номер страницы
    per_page = request.args.get('per_page', 10, type=int)  # Количество записей на странице, по умолчанию 10

    # Ограничение допустимых значений для per_page
    per_page = per_page if per_page in [10, 50, 100] else 10

    # Составляем запрос для поиска пользователей
    query = sa.select(Users).filter(
        sa.or_(
            Users.name.ilike(f'%{search_query}%'),
            Users.email.ilike(f'%{search_query}%')
        )
    )

    # Получаем общее количество пользователей
    total_count_query = sa.select(sa.func.count()).select_from(
        sa.select(Users).filter(
            sa.or_(
                Users.name.ilike(f'%{search_query}%'),
                Users.email.ilike(f'%{search_query}%')
            )
        )
    )
    total_count = db.session.execute(total_count_query).scalar()

    # Пагинация
    offset = (page - 1) * per_page
    paginated_query = query.limit(per_page).offset(offset)

    # Выполняем запрос с учетом пагинации
    users_query = db.session.execute(paginated_query)
    users = users_query.scalars().all()

    # Создаем объект пагинации вручную
    class Pagination:
        def __init__(self, total, page, per_page):
            self.total = total
            self.page = page
            self.per_page = per_page
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1
            self.next_num = page + 1

    pagination = Pagination(total_count, page, per_page)

    return render_template(
        'users/list.html',
        users=users,
        active_menu='administration',
        pagination=pagination,
        per_page=per_page
    )


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
    return render_template('users/create.html', form=form, active_menu='administration')


@users.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    user_id = current_user.get_id()
    session.pop(user_id, None)
    logout_user()
    return redirect(url_for('users.login'))


@users.route('/users/export', methods=['GET'])
@login_required
def export_users():
    # get a list of all users from the database
    users_query = db.session.execute(sa.select(Users))
    users = users_query.scalars().all()

    # Convert data to DataFrame
    user_data = [{
        "id": user.id,
        "სახელი": user.name,
        "meili": user.email,
        "შექმნის თარიღი": user.createdAt,
        "ბოლო ვიზიტი": user.lastLogin
    } for user in users]

    df = pd.DataFrame(user_data)

    # Create an Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Users')

        # Access to the active sheet
        worksheet = writer.sheets['Users']

        # Automatically change column widths
        for col in worksheet.columns:
            max_length = 0
            column = col[0].column_letter  # We get the letter designation of the column (for example, 'A')

            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))

            adjusted_width = max_length + 2  # Adding some space
            worksheet.column_dimensions[column].width = adjusted_width

    # Move the stream pointer to the beginning of the file
    output.seek(0)

    # Sending a file
    return send_file(output, as_attachment=True, download_name="users.xlsx",
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

