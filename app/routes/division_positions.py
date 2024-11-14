# crm_flask/app/controllers/division_positions.py
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..forms.division_positions import DivisionPositionCreateForm
from ..models.division_positions import DivisionPositions
from ..models.division import Divisions

division_positions = Blueprint('division_positions', __name__)


@division_positions.route('/division/<int:div_id>/positions/list', methods=['GET'])
@login_required
def positions_list(div_id):
    if 'division_positions_list' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['division_positions_list']", 'danger')
        return redirect(url_for('dashboard.index'))

    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = per_page if per_page in [10, 50, 100] else 10

    query = DivisionPositions.query.filter(
        DivisionPositions.division_id == div_id,
        DivisionPositions.name.ilike(f'%{search_query}%')
    ).order_by(DivisionPositions.created_at.desc())

    total_count = query.count()
    positions_list = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'division/positions/list.html',
        positions=positions_list.items,
        pagination=positions_list,
        div_id=div_id,
        active_menu='administration'
    )


@division_positions.route('/division/<int:div_id>/positions/create', methods=['GET', 'POST'])
@login_required
def position_create(div_id):
    if 'division_position_create' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['division_position_create']", 'danger')
        return redirect(url_for('dashboard.index'))

    division = Divisions.query.get_or_404(div_id)
    form = DivisionPositionCreateForm(division_id=div_id)

    if form.validate_on_submit():
        position = DivisionPositions(name=form.name.data, division_id=division.id)
        db.session.add(position)
        db.session.commit()
        flash('პოზიცია დამატებულია!', 'success')
        return redirect(url_for('division_positions.positions_list', div_id=div_id))

    return render_template('division/positions/create.html', form=form, division=division,
                           active_menu='administration')


@division_positions.route('/division/<int:div_id>/positions/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def position_edit(div_id, id):
    if 'division_position_edit' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['division_position_edit']", 'danger')
        return redirect(url_for('dashboard.index'))

    division = Divisions.query.get_or_404(div_id)
    position = DivisionPositions.query.get_or_404(id)
    form = DivisionPositionCreateForm(obj=position)

    if form.validate_on_submit():
        position.name = form.name.data
        db.session.commit()
        flash('პოზიცია განახლებულია!', 'success')
        return redirect(url_for('division_positions.positions_list', div_id=div_id))

    return render_template('division/positions/edit.html', form=form, division=division, position=position,
                           active_menu='administration')
