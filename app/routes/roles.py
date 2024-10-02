from flask import Blueprint, request, render_template, redirect, url_for, flash, send_file
from flask_login import login_required
import sqlalchemy as sa
import pandas as pd
from io import BytesIO
from ..extensions import db, csrf
from ..forms.roles import RoleCreateForm
from ..models.roles import Roles
from ..models.roles_permissions import RolesPermissions
from ..models.permissions import Permissions

roles = Blueprint('roles', __name__)

@roles.route('/roles/roles_list', methods=['GET', 'POST'])
@login_required
def roles_list():
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    per_page = per_page if per_page in [10, 50, 100] else 10

    # Основной запрос для ролей с подсчетом разрешений
    query = (
        sa.select(Roles, sa.func.count(RolesPermissions.permission_id).label('permissions_count'))
        .outerjoin(RolesPermissions, Roles.id == RolesPermissions.role_id)
        .filter(Roles.name.ilike(f'%{search_query}%'))
        .group_by(Roles.id)
        .order_by(Roles.created_at.desc())
    )

    total_count_query = sa.select(sa.func.count()).select_from(Roles).filter(Roles.name.ilike(f'%{search_query}%'))
    total_count = db.session.execute(total_count_query).scalar()

    offset = (page - 1) * per_page
    paginated_query = query.limit(per_page).offset(offset)

    roles_query = db.session.execute(paginated_query)
    roles_list = roles_query.all()  # Получаем список кортежей (роль, количество разрешений)

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
        'roles/roles_list.html',
        roles=roles_list,
        active_menu='administration',
        pagination=pagination,
        per_page=per_page
    )


@roles.route('/roles/create_role', methods=['GET', 'POST'])
@login_required
def create_role():
    form = RoleCreateForm()
    if form.validate_on_submit():
        role = Roles(name=form.name.data, description=form.description.data)
        db.session.add(role)
        db.session.commit()
        flash('როლი წარმატებით დაემატა!', 'success')
        return redirect(url_for('roles.roles_list'))
    return render_template('roles/create_role.html', form=form, active_menu='administration')


@roles.route('/roles/edit_role/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_role(id):
    role = db.session.execute(sa.select(Roles).filter_by(id=id)).scalar_one_or_none()
    if role is None:
        flash('როლი ვერ მოიძებნა!', 'danger')
        return redirect(url_for('roles.roles_list'))

    form = RoleCreateForm(obj=role)

    if form.validate_on_submit():
        role.name = form.name.data
        role.description = form.description.data
        db.session.commit()
        flash('როლი წარმატებით დარედაქტირდა!', 'success')
        return redirect(url_for('roles.roles_list'))

    return render_template('roles/edit_role.html', form=form, role=role, active_menu='administration')


@roles.route('/roles/export', methods=['GET'])
@login_required
def export_roles():
    roles_query = db.session.execute(sa.select(Roles))
    roles = roles_query.scalars().all()

    role_data = [{
        "id": role.id,
        "Name": role.name,
        "Description": role.description,
        "Created At": role.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for role in roles]

    df = pd.DataFrame(role_data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Roles')

    output.seek(0)

    return send_file(output, as_attachment=True, download_name="roles.xlsx",
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


# Маршрут для отображения разрешений конкретной роли
@roles.route('/roles/role/<int:id>/permissions', methods=['GET', 'POST'])
def permissions_for_role(id):
    role = Roles.query.get_or_404(id)

    # Получаем все разрешения
    all_permissions = Permissions.query.all()

    # Получаем разрешения, связанные с этой ролью
    role_permissions = {rp.permission_id for rp in RolesPermissions.query.filter_by(role_id=id).all()}

    # Если была отправка формы для добавления или удаления разрешения
    if request.method == 'POST':
        # Для добавления разрешения
        if request.form.get('add_permission'):
            permission_id = request.form.get('permission_id')
            if permission_id:
                permission = Permissions.query.get(permission_id)
                if permission:
                    # Проверяем, существует ли уже связь
                    existing_role_permission = RolesPermissions.query.filter_by(role_id=role.id,
                                                                                permission_id=permission.id).first()
                    if not existing_role_permission:
                        new_role_permission = RolesPermissions(role_id=role.id, permission_id=permission.id)
                        db.session.add(new_role_permission)
                        db.session.commit()
                        flash('დაშვება წარმატებით დამატებულია.', 'success')
                    else:
                        flash('დაშვება უკვე გააქტიურებულია როლზე.', 'danger')
                else:
                    flash('დაშვება ვერ მოიძებნა.', 'danger')

        # Для удаления разрешения
        elif request.form.get('delete_permission'):
            permission_id = request.form.get('permission_id')
            if permission_id:
                role_permission = RolesPermissions.query.filter_by(role_id=role.id, permission_id=permission_id).first()
                if role_permission:
                    db.session.delete(role_permission)
                    db.session.commit()
                    flash('დაშვება წარმატებით გათიშულია.', 'success')
                else:
                    flash('დაშვება არ არის დაკავშირებული ამ როლთან.', 'danger')

        return redirect(url_for('roles.permissions_for_role', id=role.id))

    return render_template(
        'roles/permissions_for_role.html',
        role=role,
        role_permissions=role_permissions,
        all_permissions=all_permissions,
        active_menu='administration'
    )

