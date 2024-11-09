# crm_flask/app/routes/roles.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, send_file, jsonify
from flask_login import login_required, current_user
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
    if 'roles_list' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['roles_list']", 'danger')
        return redirect(url_for('dashboard.index'))
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    per_page = per_page if per_page in [10, 50, 100] else 10

    # Basic query for roles with permission counting
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
    roles_list = roles_query.all()  # get a list of tuples (role, number of permissions)

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
    if 'roles_create' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['roles_create']", 'danger')
        return redirect(url_for('dashboard.index'))
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
    if 'roles_edit' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['roles_edit']", 'danger')
        return redirect(url_for('dashboard.index'))
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
    if 'roles_export' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['roles_export']", 'danger')
        return redirect(url_for('dashboard.index'))
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


# Route to display permissions of a specific role
@roles.route('/roles/role/<int:id>/permissions', methods=['GET', 'POST'])
def permissions_for_role(id):
    if 'roles_permissions' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['roles_permissions']", 'danger')
        return redirect(url_for('dashboard.index'))

    role = Roles.query.get_or_404(id)
    all_permissions = Permissions.query.all()
    role_permissions = {rp.permission_id for rp in RolesPermissions.query.filter_by(role_id=id).all()}

    if request.method == 'POST':
        permission_id = request.form.get('permission_id')
        if permission_id:
            permission = Permissions.query.get(permission_id)
            if not permission:
                return jsonify({'success': False, 'message': 'დაშვება ვერ მოიძებნა.'})

            # Adding permission
            if request.form.get('add_permission'):
                existing_role_permission = RolesPermissions.query.filter_by(
                    role_id=role.id, permission_id=permission.id).first()
                if not existing_role_permission:
                    new_role_permission = RolesPermissions(role_id=role.id, permission_id=permission.id)
                    db.session.add(new_role_permission)
                    db.session.commit()
                    return jsonify({'success': True, 'action': 'added'})

            # Removing permission
            elif request.form.get('delete_permission'):
                role_permission = RolesPermissions.query.filter_by(
                    role_id=role.id, permission_id=permission_id).first()
                if role_permission:
                    db.session.delete(role_permission)
                    db.session.commit()
                    return jsonify({'success': True, 'action': 'removed'})

        return jsonify({'success': False, 'message': 'დაფიქსირდა შეცდომა.'})

    return render_template(
        'roles/permissions_for_role.html',
        role=role,
        role_permissions=role_permissions,
        all_permissions=all_permissions,
        active_menu='administration'
    )
