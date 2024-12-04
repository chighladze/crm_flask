# project path: crm_flask/app/routes/task_categories.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError
import sqlalchemy as sa
from io import BytesIO
import pandas as pd
from ..extensions import db
from ..models import TaskCategories, TaskTypes
from ..forms import TaskTypeForm
from ..forms.task_category import TaskCategoryForm

# Создаем Blueprint
task_categories = Blueprint('task_categories', __name__)


# Список категорий с фильтрацией, пагинацией
@task_categories.route('/task_categories/list', methods=['GET'])
@login_required
def list_task_categories():
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = TaskCategories.query.filter(TaskCategories.name.ilike(f"%{search_query}%"))
    total_count = query.count()

    categories = query.paginate(page=page, per_page=per_page, error_out=False)

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
        'task_categories/list.html',
        categories=categories.items,
        search_query=search_query,
        pagination=pagination
    )


# Создание новой категории
@task_categories.route('/task_categories/create', methods=['GET', 'POST'])
@login_required
def create_task_category():
    form = TaskCategoryForm()
    if form.validate_on_submit():
        try:
            new_category = TaskCategories(
                name=form.name.data,
                position_id=form.position_id.data
            )
            db.session.add(new_category)
            db.session.commit()
            flash('კატეგორია წარმატებით შექმნილია!', 'success')
            return redirect(url_for('task_categories.list_task_categories'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'შეცდომა კატეგორიის შექმნისას: {str(e)}', 'danger')

    return render_template('task_categories/create.html', form=form)


# Редактирование категории
@task_categories.route('/task_categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task_category(id):
    category = TaskCategories.query.get_or_404(id)
    form = TaskCategoryForm(obj=category)

    if form.validate_on_submit():
        try:
            category.name = form.name.data
            category.position_id = form.position_id.data
            db.session.commit()
            flash('კატეგორია წარმატებით განახლდა!', 'success')
            return redirect(url_for('task_categories.list_task_categories'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'შეცდომა კატეგორიის განახლებისას: {str(e)}', 'danger')

    return render_template('task_categories/edit.html', form=form, category=category)


# Скрытие категории
@task_categories.route('/task_categories/hide/<int:id>', methods=['POST'])
@login_required
def hide_task_category(id):
    category = TaskCategories.query.get_or_404(id)
    try:
        category.is_hidden = True
        db.session.commit()
        flash('კატეგორია წარმატებით დაფარულია!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'შეცდომა კატეგორიის დაფარვისას: {str(e)}', 'danger')
    return redirect(url_for('task_categories.list_task_categories'))


# Экспорт категорий в Excel
@task_categories.route('/task_categories/export', methods=['GET'])
@login_required
def export_task_categories():
    search_query = request.args.get('search', '')

    query = TaskCategories.query.filter(TaskCategories.name.ilike(f"%{search_query}%"))
    categories = query.all()

    data = [{
        'ID': category.id,
        'Name': category.name,
        'Position': category.division_position.name if category.division_position else 'Не указана'
    } for category in categories]

    df = pd.DataFrame(data)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Categories')
        worksheet = writer.sheets['Categories']

        for col in worksheet.columns:
            max_length = max(len(str(cell.value or "")) for cell in col)
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = max_length + 2

    output.seek(0)
    return send_file(output, as_attachment=True, download_name="task_categories.xlsx",
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
