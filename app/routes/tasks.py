# crm_flask/app/routes/tasks.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
import sqlalchemy as sa
from ..extensions import db
from ..models import Tasks, TaskStatuses, TaskPriorities, Users, TaskTypes
from ..forms import TaskForm
import pandas as pd
from io import BytesIO

tasks = Blueprint('tasks', __name__)


@tasks.route('/tasks/details/<int:task_id>')
def task_details(task_id):
    task = Tasks.query.get_or_404(task_id)
    statuses = TaskStatuses.query.all()  # Все доступные статусы

    return jsonify({
        'id': task.id,
        'description': task.description,
        'created_user': task.created_user.name if task.created_user else 'უცნობი',
        'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
        'progress': task.progress,
        'current_status': {'id': task.status_id, 'name': task.status.name},
        'statuses': [{'id': status.id, 'name': status.name} for status in statuses],
    })
@tasks.route('/tasks/update/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    task = Tasks.query.get_or_404(task_id)
    status_id = request.form.get('status')

    if status_id:
        try:
            task.status_id = int(status_id)
            db.session.commit()
            return jsonify({'message': 'სტატუსი წარმატებით განახლდა!'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'შეცდომა: {str(e)}'}), 400
    else:
        return jsonify({'message': 'არასწორი სტატუსი'}), 400



@tasks.route('/tasks/view/<int:task_id>', methods=['GET', 'POST'])
@login_required
def view_task(task_id):
    # Получаем задачу с необходимыми данными
    task = Tasks.query.get_or_404(task_id)
    form = TaskForm(obj=task)

    form.task_type_id.choices = [(type.id, type.name) for type in TaskTypes.query.all()]
    form.status_id.choices = [(status.id, status.name) for status in TaskStatuses.query.all()]
    form.task_priority_id.choices = [(priority.id, priority.level) for priority in TaskPriorities.query.all()]
    form.assigned_to.choices = [(user.id, user.name) for user in Users.query.all()]
    form.completed_by.choices = [(user.id, user.name) for user in Users.query.all()]

    # Настраиваем поля только для чтения
    form.task_category_id.render_kw = {'readonly': True, 'disabled': True}
    form.task_type_id.render_kw = {'readonly': True, 'disabled': True}
    form.description.render_kw = {'readonly': True, 'disabled': True}
    form.created_by.render_kw = {'readonly': True, 'disabled': True}
    form.completed_by.render_kw = {'readonly': True, 'disabled': True}

    if form.validate_on_submit():
        try:
            task.status_id = form.status_id.data
            task.task_priority_id = form.task_priority_id.data
            task.due_date = form.due_date.data
            task.progress = form.progress.data
            task.assigned_to = form.assigned_to.data

            db.session.commit()
            flash("Задача успешно обновлена!", "success")
            return redirect(url_for('tasks.tasks_list'))
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при обновлении задачи: {str(e)}", "danger")

    return render_template(
        'tasks/view_task.html',
        form=form,
        task=task,
        creator_name=task.created_user.name if task.created_user else "Неизвестный пользователь",
        created_division=task.created_division_id,
        completed_division=task.completed_division_id,
        estimated_time=task.estimated_time,
        actual_time=task.actual_time,
        parent_task=task.parent_task_id,
        comments_count=task.comments_count,
        is_recurring=task.is_recurring,
        active_menu='tasks'
    )


@tasks.route('/tasks/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Tasks.query.get_or_404(task_id)

    form = TaskForm(obj=task)

    form.status_id.choices = [(status.id, status.name) for status in TaskStatuses.query.all()]
    form.task_priority_id.choices = [(priority.id, priority.level) for priority in TaskPriorities.query.all()]

    if form.validate_on_submit():
        try:
            task.task_category_id = form.task_category_id.data
            task.description = form.description.data
            task.status_id = form.status_id.data
            task.task_priority_id = form.task_priority_id.data
            task.due_date = form.due_date.data

            db.session.commit()
            flash("Задача успешно обновлена!", "success")
            return redirect(url_for('tasks.tasks_list'))
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при редактировании задачи: {str(e)}", "danger")

    return render_template(
        'tasks/edit_task.html',
        form=form,
        task=task,
        active_menu='tasks'
    )


@tasks.route('/tasks/list', methods=['GET'])
@login_required
def tasks_list():
    search_query = request.args.get('search', '')
    status_id = request.args.get('status_id', type=int)
    task_category_id = request.args.get('task_category_id', type=int)
    priority_id = request.args.get('priority_id', type=int)
    created_by = request.args.get('created_by', type=int)
    assigned_to = request.args.get('assigned_to', type=int)
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Tasks.query

    # Применение фильтров
    if search_query:
        query = query.filter(Tasks.description.ilike(f'%{search_query}%'))
    if status_id:
        query = query.filter(Tasks.status_id == status_id)
    if task_category_id:
        query = query.filter(Tasks.task_category_id == task_category_id)
    if priority_id:
        query = query.filter(Tasks.task_priority_id == priority_id)
    if created_by:
        query = query.filter(Tasks.created_by == created_by)
    if assigned_to:
        query = query.filter(Tasks.assigned_to == assigned_to)
    if start_date:
        query = query.filter(Tasks.created_at >= start_date)
    if end_date:
        query = query.filter(Tasks.created_at <= end_date)

    # Пагинация
    tasks_list = query.paginate(page=page, per_page=per_page)

    # Данные для фильтров
    statuses = TaskStatuses.query.all()
    priorities = TaskPriorities.query.all()
    users = Users.query.all()  # Загрузка списка пользователей

    return render_template(
        'tasks/task_list.html',
        tasks=tasks_list.items,
        pagination=tasks_list,
        statuses=statuses,
        priorities=priorities,
        users=users,
        search_query=search_query,
        status_id=status_id,
        task_category_id=task_category_id,
        priority_id=priority_id,
        created_by=created_by,
        assigned_to=assigned_to,
        start_date=start_date,
        end_date=end_date,
        per_page=per_page
    )


@tasks.route('/tasks/export', methods=['GET'])
@login_required
def export():
    tasks = Tasks.query.all()
    task_data = [{
        'ID': task.id,
        'Описание': task.description,
        'Статус': task.status.name if task.status else '',
        'Приоритет': task.priority.name if task.priority else '',
        'Дата создания': task.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for task in tasks]

    df = pd.DataFrame(task_data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Tasks')

    output.seek(0)
    return send_file(output, as_attachment=True, download_name='tasks_list.xlsx')


@tasks.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    from ..forms.tasks import TaskForm
    form = TaskForm()

    # Adding categories to the form choices so they are available in the dropdown
    form.task_category_id.choices = [(category.id, category.name) for category in categories]

    if form.validate_on_submit():
        try:
            task = Tasks(
                task_category_id=form.task_category_id.data,
                description=form.description.data,
                status_id=form.status_id.data,
                created_by=current_user.id,
                due_date=form.due_date.data,
                task_priority_id=form.task_priority_id.data
            )
            db.session.add(task)
            db.session.commit()
            flash("დავალება წარმატებით შეიქმნა!", "success")
            return redirect(url_for('tasks.tasks_list'))
        except Exception as e:
            db.session.rollback()
            flash(f"დავალების შექმნის შეცდომა: {str(e)}", "danger")

    return render_template(
        'tasks/create_task.html',
        form=form,
        active_menu='tasks'
    )
