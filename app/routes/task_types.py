# project path: crm_flask/app/routes/task_types.py

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

task_types = Blueprint('task_types', __name__)


@task_types.route('/task_types/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task_type(id):
    task_type = TaskTypes.query.get_or_404(id)
    form = TaskTypeForm(obj=task_type)

    if form.validate_on_submit():
        try:
            task_type.name = form.name.data
            db.session.commit()
            flash('Тип категории успешно обновлён!', 'success')
            return redirect(url_for('task_categories.list_task_categories'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении типа категории: {str(e)}', 'danger')

    return render_template('task_types/edit.html', form=form, task_type=task_type)


@task_types.route('/create/<int:category_id>', methods=['GET', 'POST'])
@login_required
def create_task_type(category_id):
    form = TaskTypeForm()
    if form.validate_on_submit():
        try:
            new_type = TaskTypes(
                name=form.name.data,
                category_id=category_id
            )
            db.session.add(new_type)
            db.session.commit()
            flash('Тип категории успешно создан!', 'success')
            return redirect(url_for('task_categories.list_task_categories'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Ошибка при создании типа категории: {str(e)}', 'danger')

    return render_template('task_types/create.html', form=form)
