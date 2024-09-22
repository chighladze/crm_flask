from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required
import sqlalchemy as sa
from ..extensions import db
from ..forms.department_positions import DepartmentPositionCreateForm
from ..models.department_positions import DepartmentPositions

department_positions = Blueprint('department_positions', __name__)


@department_positions.route('/departments/<int:dep_id>/positions/list', methods=['GET'])
@login_required
def list(dep_id):
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Ограничение допустимых значений для per_page
    per_page = per_page if per_page in [10, 50, 100] else 10

    # Составляем запрос для поиска позиций в определённом департаменте
    query = sa.select(DepartmentPositions).filter(
        DepartmentPositions.department_id == dep_id,
        sa.or_(
            DepartmentPositions.name.ilike(f'%{search_query}%')
        )
    ).order_by(DepartmentPositions.created_at.desc())

    # Получаем общее количество позиций для пагинации
    total_count_query = sa.select(sa.func.count()).select_from(
        sa.select(DepartmentPositions).filter(
            DepartmentPositions.department_id == dep_id,
            sa.or_(
                DepartmentPositions.name.ilike(f'%{search_query}%')
            )
        )
    )
    total_count = db.session.execute(total_count_query).scalar()

    # Пагинация
    offset = (page - 1) * per_page
    paginated_query = query.limit(per_page).offset(offset)

    # Выполняем запрос с учетом пагинации
    positions_query = db.session.execute(paginated_query)
    positions_list = positions_query.scalars().all()

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
        'departments/positions/list.html',
        positions=positions_list,
        dep_id=dep_id,
        pagination=pagination,
        per_page=per_page
    )


@department_positions.route('/positions/create', methods=['GET', 'POST'])
@login_required
def create():
    form = DepartmentPositionCreateForm()
    if form.validate_on_submit():
        position = DepartmentPositions(name=form.name.data, description=form.description.data,
                                       department_id=form.department_id.data)
        db.session.add(position)
        db.session.commit()
        flash('პოზიცია წარმატებით დაემატა!', 'success')
        return redirect(url_for('department_positions.list', dep_id=form.department_id.data))
    return render_template('departments/positions/create.html', form=form, active_menu='administration')
