from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
import sqlalchemy as sa
from ..extensions import db
from ..forms.division import DivisionCreateForm
from ..models.division import Divisions
from ..models.departments import Departments

divisions = Blueprint('divisions', __name__)


@divisions.route('/departments/<int:dep_id>/divisions/list', methods=['GET'])
@login_required
def div_list(dep_id):
    if 'divisions_list' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['divisions_list']", 'danger')
        return redirect(url_for('dashboard.index'))
    # Получаем данные о департаменте
    department_query = sa.select(Departments).where(Departments.id == dep_id)
    department = db.session.execute(department_query).scalar_one_or_none()

    # Проверяем, существует ли департамент
    if department is None:
        # Можно перенаправить на страницу с ошибкой или на другую страницу
        return "Department not found", 404

    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Ограничиваем per_page значениями 10, 50, 100
    per_page = per_page if per_page in [10, 50, 100] else 10

    # Фильтрация подразделений по ID департамента
    query = sa.select(Divisions).where(Divisions.department_id == dep_id).order_by(Divisions.created_at.desc())

    # Если есть строка поиска, добавляем фильтрацию по названию подразделения
    if search_query:
        query = query.where(Divisions.name.ilike(f'%{search_query}%'))

    # Получаем общее количество подразделений для данного департамента
    total_count_query = sa.select(sa.func.count()).select_from(Divisions).where(Divisions.department_id == dep_id)
    if search_query:
        total_count_query = total_count_query.where(Divisions.name.ilike(f'%{search_query}%'))

    total_count = db.session.execute(total_count_query).scalar()

    # Пагинация
    offset = (page - 1) * per_page
    paginated_query = query.limit(per_page).offset(offset)

    # Выполняем запрос с учетом пагинации
    divisions_query = db.session.execute(paginated_query)
    divisions_list = divisions_query.scalars().all()

    # Пагинация вручную
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
        'division/list.html',
        divisions=divisions_list,
        active_menu='administration',
        pagination=pagination,
        department=department,  # Теперь это экземпляр Department, а не запрос
        per_page=per_page,
    )


@divisions.route('/departments/<int:dep_id>/divisions/create', methods=['GET', 'POST'])
@login_required
def create(dep_id):
    if 'divisions_create' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['divisions_create']", 'danger')
        return redirect(url_for('dashboard.index'))
    department = Departments.query.get_or_404(dep_id)
    form = DivisionCreateForm(department_id=department.id)

    if form.validate_on_submit():
        division = Divisions(
            name=form.name.data,
            description=form.description.data,
            department_id=department.id
        )
        db.session.add(division)
        db.session.commit()
        flash(f'განყოფილება ({form.name.data}) დამატებულია!', 'success')
        return redirect(url_for('divisions.div_list', dep_id=department.id))
    else:
        return render_template('division/create.html', form=form, department=department, active_menu='administration')


@divisions.route('/departments/divisions/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if 'divisions_edit' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['divisions_edit']", 'danger')
        return redirect(url_for('dashboard.index'))
    # Получаем подразделение для редактирования
    division = db.session.execute(sa.select(Divisions).filter_by(id=id)).scalar_one_or_none()
    if division is None:
        flash('განყოფილება ვერ მოიძებნა!', 'danger')
        return redirect(url_for('divisions.div_list'))

    # Создаем форму с текущими данными подразделения
    form = DivisionCreateForm(department_id=division.department_id)

    if form.validate_on_submit():
        # Обновляем данные подразделения
        division.name = form.name.data
        division.description = form.description.data
        db.session.commit()
        flash('განყოფილება წარმატებით განახლდა!', 'success')
        return redirect(url_for('divisions.div_list', dep_id=division.department_id))

    return render_template('division/edit.html', form=form, division=division, active_menu='administration')
