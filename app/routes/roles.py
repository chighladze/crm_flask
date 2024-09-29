from flask import Blueprint, request, render_template, redirect, url_for, flash, send_file
from flask_login import login_required
import sqlalchemy as sa
import pandas as pd
from io import BytesIO
from ..extensions import db
from ..forms.roles import RoleCreateForm
from ..models.roles import Roles

roles = Blueprint('roles', __name__)


@roles.route('/roles/roles_list', methods=['GET', 'POST'])
@login_required
def roles_list():
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    per_page = per_page if per_page in [10, 50, 100] else 10

    query = sa.select(Roles).filter(Roles.name.ilike(f'%{search_query}%')).order_by(Roles.created_at.desc())

    total_count_query = sa.select(sa.func.count()).select_from(Roles).filter(Roles.name.ilike(f'%{search_query}%'))
    total_count = db.session.execute(total_count_query).scalar()

    offset = (page - 1) * per_page
    paginated_query = query.limit(per_page).offset(offset)

    roles_query = db.session.execute(paginated_query)
    roles_list = roles_query.scalars().all()

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
