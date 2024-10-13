from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
import sqlalchemy as sa
from ..extensions import db
from ..forms.department_positions import DepartmentPositionCreateForm
from ..models.department_positions import DepartmentPositions
from ..models.departments import Departments

department_positions = Blueprint('department_positions', __name__)


@department_positions.route('/departments/<int:dep_id>/positions/list', methods=['GET'])
@login_required
def positions_llist(dep_id):
    if 'positions_llist' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['positions_llist']", 'danger')
        return redirect(url_for('dashboard.index'))
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Limiting allowed values ​​for per_page
    per_page = per_page if per_page in [10, 50, 100] else 10

    # create a query to search for positions in a specific department
    query = sa.select(DepartmentPositions).filter(
        DepartmentPositions.department_id == dep_id,
        sa.or_(
            DepartmentPositions.name.ilike(f'%{search_query}%')
        )
    ).order_by(DepartmentPositions.created_at.desc())

    # get the total number of positions for pagination
    total_count_query = sa.select(sa.func.count()).select_from(
        sa.select(DepartmentPositions).filter(
            DepartmentPositions.department_id == dep_id,
            sa.or_(
                DepartmentPositions.name.ilike(f'%{search_query}%')
            )
        )
    )
    total_count = db.session.execute(total_count_query).scalar()

    # Pagination
    offset = (page - 1) * per_page
    paginated_query = query.limit(per_page).offset(offset)

    # execute a query taking into account paginatio
    positions_query = db.session.execute(paginated_query)
    positions_list = positions_query.scalars().all()

    # Create a pagination object manually
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
        per_page=per_page,
        active_menu='administration'
    )


@department_positions.route('/departments/<int:dep_id>/positions/create', methods=['GET', 'POST'])
@login_required
def position_create(dep_id):
    if 'position_create' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['position_create']", 'danger')
        return redirect(url_for('dashboard.index'))
    department = Departments.query.get_or_404(dep_id)
    form = DepartmentPositionCreateForm(dep_id)
    if form.validate_on_submit():
        position = DepartmentPositions(name=form.name.data,
                                       department_id=department.id)
        db.session.add(position)
        db.session.commit()
        flash('პოზიცია წარმატებით დაემატა!', 'success')
        return redirect(url_for('department_positions.positions_llist', dep_id=form.department_id.data))
    return render_template('departments/positions/create.html',
                           form=form,
                           department=department,
                           active_menu='administration')


@department_positions.route('/departments/<int:dep_id>/positions/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def position_edit(dep_id, id):
    if 'position_edit' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['position_edit']", 'danger')
        return redirect(url_for('dashboard.index'))
    department = Departments.query.get_or_404(dep_id)
    position = DepartmentPositions.query.get_or_404(id)
    form = DepartmentPositionCreateForm(dep_id, obj=position)

    if form.validate_on_submit():
        position.name = form.name.data
        position.description = form.description.data
        db.session.commit()
        flash('პოზიცია წარმატებით განახლდა!', 'success')
        return redirect(url_for('department_positions.positions_llist', dep_id=dep_id))

    return render_template('departments/positions/edit.html', form=form, department=department, position=position,
                           active_menu='administration')
