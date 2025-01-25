# crm_flask/app/routes/tasks.py
import uuid
import sqlalchemy as sa
from io import BytesIO
import pandas as pd

from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, send_file
from flask_wtf import csrf
from flask_login import login_required, current_user

from ..extensions import db
from ..models import Tasks, TaskStatuses, TaskPriorities, TaskTypes, Divisions, TaskComments
from ..models.users import Users
from ..models import CustomerAccount
from ..forms import TaskForm

tasks = Blueprint('tasks', __name__)


# ------------- AJAX эндпоинты для раздела задач ---------------

@tasks.route('/tasks/get_csrf_token', methods=['GET'])
def get_csrf_token():
    token = csrf.generate_csrf()
    return jsonify({'csrf_token': token})


@tasks.route('/tasks/get_divisions', methods=['GET'])
@login_required
def get_divisions():
    """
    Returns a list of all available divisions.
    """
    divisions = Divisions.query.all()
    divisions_data = [{'id': division.id, 'name': division.name} for division in divisions]
    return jsonify({'divisions': divisions_data}), 200


@tasks.route('/tasks/task_types/get_task_types/<int:division_id>', methods=['GET'])
@login_required
def get_task_types_by_division(division_id):
    """
    Returns a list of task types for the specified division.
    """
    task_types = TaskTypes.query.filter_by(division_id=division_id).all()
    task_types_data = [{'id': t.id, 'name': t.name} for t in task_types]
    return jsonify({'task_types': task_types_data}), 200


@tasks.route('/tasks/details/<int:task_id>', methods=['GET'])
@login_required
def task_details(task_id):
    """
    Returns detailed information about a specific task.
    """
    task = Tasks.query.get_or_404(task_id)
    statuses = TaskStatuses.query.all()

    if task.task_type and getattr(task.task_type, 'division', None):
        task_types = TaskTypes.query.filter_by(division_id=task.task_type.division_id).all()
    else:
        task_types = TaskTypes.query.all()

    mac_address = ''
    if task.order and getattr(task.order, 'customer_account', None):
        account = task.order.customer_account
        mac_address = account.mac_address if account.mac_address else ''

    return jsonify({
        'id': task.id,
        'description': task.description,
        'created_user': task.created_user.name if task.created_user else 'უცნობი',
        'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
        'progress': task.progress,
        'current_status': {
            'id': task.status_id,
            'name': task.status.name,
            'bootstrap_class': task.status.bootstrap_class
        },
        'task_type': {
            'id': task.task_type.id if task.task_type else None,
            'name': task.task_type.name if task.task_type else None,
            'division': {
                'id': task.task_type.division.id,
                'name': task.task_type.division.name
            } if task.task_type and getattr(task.task_type, 'division', None) else {}
        },
        'customer_id': task.order.customer_id if task.order else None,
        'statuses': [{'id': status.id, 'name': status.name} for status in statuses],
        'task_types': [{'id': t.id, 'name': t.name} for t in task_types],
        'mac_address': mac_address
    }), 200


@tasks.route('/tasks/update/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    """
    განახლებს დავალების სტატუსს და ქმნის ასაინერი.
    """
    task = Tasks.query.get_or_404(task_id)
    data = request.get_json()

    status_id = data.get('status_id')
    assigned_to = data.get('assigned_to')

    if not status_id:
        return jsonify({'message': 'სტატუსი აუცილებელია.'}), 400

    try:
        # განახლება სტატუსი
        status = TaskStatuses.query.get(status_id)
        if not status:
            return jsonify({'message': 'სათანაზღაურებული სტატუსის ID არასწორია.'}), 400

        task.status_id = status_id

        # განახლება ასაინერი
        if assigned_to:
            user = Users.query.get(assigned_to)
            if not user:
                return jsonify({'message': 'ასაინერი ID არასწორია.'}), 400
            task.assigned_to = assigned_to
        else:
            task.assigned_to = None  # ასაინერის ამოშლა

        db.session.commit()

        response = {
            'message': 'დავალება წარმატებით განახლდა!',
            'new_status': {
                'id': task.status.id,
                'name': task.status.name,
                'bootstrap_class': task.status.bootstrap_class
            },
            'assigned_user': {
                'id': task.assigned_user.id if task.assigned_user else None,
                'name': task.assigned_user.name if task.assigned_user else 'გამიზენილი არაა'
            }
        }

        return jsonify(response), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'შეცდომა: {str(e)}'}), 500


@tasks.route('/tasks/<int:task_id>/add_comment', methods=['POST'])
@login_required
def add_comment(task_id):
    """
    დამატება კომენტარი დავალებას.
    """
    task = Tasks.query.get_or_404(task_id)
    data = request.get_json()
    content = data.get('content', '').strip()

    if not content:
        return jsonify({'message': 'კომენტარი არ უნდა იყოს ცარიელი.'}), 400

    try:
        comment = TaskComments(task_id=task_id, user_id=current_user.id, content=content)
        db.session.add(comment)
        db.session.commit()

        response = {
            'message': 'კომენტარი წარმატებით დამატებულია.',
            'comment': {
                'id': comment.id,
                'user': current_user.name,  # დარწმუნდით, რომ Users მოდელს აქვს name ველი
                'content': comment.content,
                'timestamp': comment.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
        }

        return jsonify(response), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'შეცდომა: {str(e)}'}), 500


@tasks.route('/tasks/view/<int:task_id>', methods=['GET'])
@login_required
def view_task(task_id):
    task = Tasks.query.get_or_404(task_id)
    form = TaskForm(obj=task)

    form.task_type_id.choices = [(t.id, t.name) for t in TaskTypes.query.all()]
    form.status_id.choices = [(s.id, s.name) for s in TaskStatuses.query.all()]
    form.task_priority_id.choices = [(p.id, p.level) for p in TaskPriorities.query.all()]
    form.assigned_to.choices = [(u.id, u.name) for u in Users.query.all()]
    form.completed_by.choices = [(u.id, u.name) for u in Users.query.all()]

    form.task_category_id.render_kw = {'readonly': True, 'disabled': True}
    form.task_type_id.render_kw = {'readonly': True, 'disabled': True}
    form.description.render_kw = {'readonly': True, 'disabled': True}
    form.created_by.render_kw = {'readonly': True, 'disabled': True}
    form.completed_by.render_kw = {'readonly': True, 'disabled': True}

    # Получаем комментарии, сортированные по дате
    comments = task.comments.order_by(TaskComments.timestamp.asc()).all()

    return render_template('tasks/view_task.html', form=form, task=task, comments=comments)


@tasks.route('/tasks/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Tasks.query.get_or_404(task_id)
    form = TaskForm(obj=task)

    form.status_id.choices = [(s.id, s.name) for s in TaskStatuses.query.all()]
    form.task_priority_id.choices = [(p.id, p.level) for p in TaskPriorities.query.all()]

    if form.validate_on_submit():
        try:
            task.task_category_id = form.task_category_id.data
            task.description = form.description.data
            task.status_id = form.status_id.data
            task.task_priority_id = form.task_priority_id.data
            task.due_date = form.due_date.data

            db.session.commit()
            flash("დავალება წარმატებით განახლდა!", "success")
            return redirect(url_for('tasks.tasks_list'))
        except Exception as e:
            db.session.rollback()
            flash(f"შეცდომა რედაქტირებისას: {str(e)}", "danger")

    return render_template('tasks/edit_task.html', form=form, task=task)


# ------------- Страница и API для списка задач ---------------

@tasks.route('/tasks/list', methods=['GET'])
@login_required
def tasks_list():
    """
    Отображает страницу со списком задач с фильтрацией и пагинацией.
    """
    search_query = request.args.get('search', '')
    status_id = request.args.get('status_id', type=int)
    task_category_id = request.args.get('task_category_id', type=int)
    priority_id = request.args.get('priority_id', type=int)
    created_by = request.args.get('created_by', type=int)
    assigned_to = request.args.get('assigned_to', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    due_date_start = request.args.get('due_date_start')
    due_date_end = request.args.get('due_date_end')
    created_division_id = request.args.get('created_division_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Tasks.query

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
    if due_date_start:
        query = query.filter(Tasks.due_date >= due_date_start)
    if due_date_end:
        query = query.filter(Tasks.due_date <= due_date_end)
    if created_division_id:
        query = query.filter(Tasks.created_division_id == created_division_id)

    tasks_paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    statuses = TaskStatuses.query.all()
    priorities = TaskPriorities.query.all()
    users = Users.query.all()
    categories = TaskTypes.query.all()  # Используем TaskTypes как категории
    divisions = Divisions.query.all()

    return render_template(
        'tasks/task_list.html',
        tasks=tasks_paginated.items,
        pagination=tasks_paginated,
        statuses=statuses,
        priorities=priorities,
        users=users,
        categories=categories,
        divisions=divisions,
        search_query=search_query,
        status_id=status_id,
        task_category_id=task_category_id,
        priority_id=priority_id,
        created_by=created_by,
        assigned_to=assigned_to,
        start_date=start_date,
        end_date=end_date,
        due_date_start=due_date_start,
        due_date_end=due_date_end,
        created_division_id=created_division_id,
        per_page=per_page
    )


@tasks.route('/api/tasks_list', methods=['GET'])
@login_required
def api_tasks_list():
    search_query = request.args.get('search', '')
    status_id = request.args.get('status_id', type=int)
    task_category_id = request.args.get('task_category_id', type=int)
    priority_id = request.args.get('priority_id', type=int)
    created_by = request.args.get('created_by', type=int)
    assigned_to = request.args.get('assigned_to', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    due_date_start = request.args.get('due_date_start')
    due_date_end = request.args.get('due_date_end')
    created_division_id = request.args.get('created_division_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Tasks.query

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
    if due_date_start:
        query = query.filter(Tasks.due_date >= due_date_start)
    if due_date_end:
        query = query.filter(Tasks.due_date <= due_date_end)
    if created_division_id:
        query = query.filter(Tasks.created_division_id == created_division_id)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    tasks_items = pagination.items

    tasks_data = [{
        "id": task.id,
        "task_category": task.task_type.name if task.task_type else '',
        "task_type": task.task_type.name if task.task_type else '',
        "status": task.status.name if task.status else 'არ არის მითითებული',
        "priority": task.priority.level if task.priority else 'არ არის მითითებული',
        "assigned_to": task.assigned_user.name if hasattr(task,
                                                          'assigned_user') and task.assigned_user else 'არ არის მითითებული',
        "created_at": task.created_at.strftime('%Y-%m-%d') if task.created_at else '',
        "due_date": task.due_date.strftime('%Y-%m-%d') if task.due_date else ''
    } for task in tasks_items]

    response = {
        "tasks": tasks_data,
        "pagination": {
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": pagination.page,
            "per_page": pagination.per_page,
            "has_prev": pagination.has_prev,
            "has_next": pagination.has_next,
        }
    }
    return jsonify(response)


@tasks.route('/tasks/export', methods=['GET'])
@login_required
def export():
    """
    Exports filtered task data to an Excel file.
    Фильтры берутся из GET-параметров, как и в маршруте для списка задач.
    """
    # Получаем параметры фильтрации из GET-запроса
    search_query = request.args.get('search', '')
    status_id = request.args.get('status_id', type=int)
    task_category_id = request.args.get('task_category_id', type=int)
    priority_id = request.args.get('priority_id', type=int)
    created_by = request.args.get('created_by', type=int)
    assigned_to = request.args.get('assigned_to', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    due_date_start = request.args.get('due_date_start')
    due_date_end = request.args.get('due_date_end')
    created_division_id = request.args.get('created_division_id', type=int)

    query = Tasks.query
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
    if due_date_start:
        query = query.filter(Tasks.due_date >= due_date_start)
    if due_date_end:
        query = query.filter(Tasks.due_date <= due_date_end)
    if created_division_id:
        query = query.filter(Tasks.created_division_id == created_division_id)

    tasks_query = query.all()

    task_data = [{
        'ID': task.id,
        'აღწერა': task.description,
        'სტატუსი': task.status.name if task.status else '',
        'პრიორიტეტი': task.priority.level if task.priority else '',
        'შექმნის თარიღი': task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'დასრულების თარიღი': task.due_date.strftime('%Y-%m-%d') if task.due_date else '',
        'დივიზია': task.created_division.name if getattr(task, 'created_division', None) else ''
    } for task in tasks_query]

    df = pd.DataFrame(task_data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Tasks')
    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name='tasks_list.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@tasks.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    """
    Renders a page to create a new task using WTForms.
    """
    from ..forms.tasks import TaskForm  # Импорт формы
    form = TaskForm()

    # Если категорий пока нет, передадим пустой список
    categories = []
    form.task_category_id.choices = [(category.id, category.name) for category in categories]
    form.status_id.choices = [(s.id, s.name) for s in TaskStatuses.query.all()]
    form.task_priority_id.choices = [(p.id, p.level) for p in TaskPriorities.query.all()]
    form.assigned_to.choices = [(u.id, u.name) for u in Users.query.all()]

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
            flash(f"შეცდომა დავალების შექმნისას: {str(e)}", "danger")
    return render_template('tasks/create_task.html', form=form)


@tasks.route('/tasks/create_subtask', methods=['POST'])
@login_required
def create_subtask():
    """
    Creates a subtask if the parent's status and task type are both 3.
    """
    data = request.get_json()
    parent_task_id = data.get('parent_task_id')
    description = data.get('description')
    task_type_id = data.get('task_type_id')
    order_id = data.get('order_id')
    mac_address = data.get('mac_address')

    try:
        parent_task_type_id = int(data.get('parent_task_type_id'))
        parent_status_change_id = int(data.get('parent_status_change_id'))
    except (ValueError, TypeError):
        return jsonify({'message': 'მიღებული მონაცემები არ არის სწორად ფორმატირებული.'}), 400

    parent_task = Tasks.query.get(parent_task_id)
    if not parent_task:
        return jsonify({'message': 'მთავარი დავალება ვერ მოიძებნა.'}), 404

    try:
        if parent_task_type_id == 3 and parent_status_change_id == 3:
            if not mac_address:
                return jsonify({'message': 'MAC-მისამართი აუცილებელია ამ STATუსისა და TIPის დავალებისთვის.'}), 400
            duplicate_mac = CustomerAccount.query.filter_by(mac_address=mac_address).first()
            if duplicate_mac:
                return jsonify({'message': 'MAC-მისამართი უკვე გამოყენებულია.', 'field': 'mac_address'}), 400

        subtask = Tasks(
            parent_task_id=parent_task_id,
            description=description,
            task_type_id=int(task_type_id),
            created_by=current_user.id,
            order_id=order_id
        )
        db.session.add(subtask)
        db.session.commit()

        parent_task.status_id = parent_status_change_id
        db.session.add(parent_task)
        db.session.commit()

        response = {
            'subtask': {
                'id': subtask.id,
                'description': subtask.description,
                'status': {
                    'id': subtask.status.id,
                    'name': subtask.status.name,
                    'bootstrap_class': subtask.status.bootstrap_class
                },
                'task_type': {
                    'id': subtask.task_type.id,
                    'name': subtask.task_type.name,
                    'division': {
                        'id': subtask.task_type.division.id,
                        'name': subtask.task_type.division.name
                    } if subtask.task_type and getattr(subtask.task_type, 'division', None) else {}
                },
                'created_user': {
                    'name': subtask.created_user.name if subtask.created_user else 'Unknown'
                },
                'created_at': subtask.created_at.strftime('%Y-%m-%d %H:%M:%S')
            },
            'new_status': {
                'id': parent_task.status_id,
                'name': parent_task.status.name,
                'bootstrap_class': parent_task.status.bootstrap_class
            },
            'customer_account': None
        }
        return jsonify(response), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'შეცდომა: {str(e)}'}), 500
