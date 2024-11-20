# crm_flask/app/routes/tasks.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
import sqlalchemy as sa
from ..extensions import db
from ..models import Tasks, TaskCategories, TaskStatuses, TaskPriorities, Users
import pandas as pd
from io import BytesIO

tasks = Blueprint('tasks', __name__)


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
    categories = TaskCategories.query.all()
    users = Users.query.all()  # Загрузка списка пользователей

    return render_template(
        'tasks/task_list.html',
        tasks=tasks_list.items,
        pagination=tasks_list,
        statuses=statuses,
        priorities=priorities,
        categories=categories,
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
    from ..forms.tasks import TaskCreateForm
    form = TaskCreateForm()

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
            flash("Задача успешно создана!", "success")
            return redirect(url_for('tasks.tasks_list'))
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при создании задачи: {str(e)}", "danger")

    return render_template(
        'tasks/create_task.html',
        form=form,
        active_menu='tasks'
    )

