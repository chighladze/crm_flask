from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from ..extensions import db
from ..models.task_categories import TaskCategories
from ..forms.task_category import TaskCategoryForm

task_categories = Blueprint('task_categories', __name__)


@task_categories.route('/task_categories/list', methods=['GET'])
@login_required
def list_task_categories():
    search_query = request.args.get('search', '')
    categories = TaskCategories.query.filter(
        TaskCategories.name.ilike(f'%{search_query}%')
    ).all()
    return render_template('task_categories/list.html', categories=categories)


@task_categories.route('/task_categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task_category(id):
    category = TaskCategories.query.get_or_404(id)
    form = TaskCategoryForm(obj=category)

    if form.validate_on_submit():
        category.name = form.name.data
        category.position_id = form.position_id.data
        db.session.commit()
        flash('Категория успешно обновлена!', 'success')
        return redirect(url_for('task_categories.list_task_categories'))

    return render_template('task_categories/edit.html', form=form, category=category)


@task_categories.route('/task_categories/create', methods=['GET', 'POST'])
@login_required
def create_task_category():
    form = TaskCategoryForm()
    if form.validate_on_submit():
        new_category = TaskCategories(name=form.name.data, position_id=form.position_id.data)
        db.session.add(new_category)
        db.session.commit()
        flash('Новая категория успешно создана!', 'success')
        return redirect(url_for('task_categories.list_task_categories'))

    return render_template('task_categories/create.html', form=form)


@task_categories.route('/task_categories/hide/<int:id>', methods=['POST'])
@login_required
def hide_task_category(id):
    category = TaskCategories.query.get_or_404(id)
    category.is_hidden = True
    db.session.commit()
    flash('Категория успешно скрыта!', 'success')
    return redirect(url_for('task_categories.list_task_categories'))
