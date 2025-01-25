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


# ------------- AJAX endpoints for tasks section ---------------

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
        'statuses': [{'id': status.id, 'name': status.name_geo} for status in statuses],
        'task_types': [{'id': t.id, 'name': t.name} for t in task_types],
        'mac_address': mac_address
    }), 200


@tasks.route('/tasks/update/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    """
    Updates the task status and, if necessary, creates a new subtask.
    """
    task = Tasks.query.get_or_404(task_id)
    data = request.get_json()

    status_id = data.get('status_id')
    assigned_to = data.get('assigned_to')

    if not status_id:
        return jsonify({'message': 'სტატუსი აუცილებელია.'}), 400

    try:
        # Process status_id
        status = TaskStatuses.query.get(status_id)
        if not status:
            return jsonify({'message': 'სტატუსის ID არასწორია.'}), 400

        # Update task status
        task.status_id = status_id

        # Process assigned_to
        if assigned_to:
            try:
                assigned_to = int(assigned_to)
            except ValueError:
                return jsonify({'message': 'შემსრულებლის ID უნდა იყოს მთელი რიცხვი.'}), 400

            user = Users.query.get(assigned_to)
            if not user:
                return jsonify({'message': 'შემსრულებლის ID არასწორია.'}), 400
            task.assigned_to = assigned_to
        else:
            task.assigned_to = None  # Remove assignee

        # Logic to create subtask under certain conditions
        new_task = None
        if status_id == '3' and task.task_type_id == 1:
            # Create a subtask with necessary fields
            new_task = Tasks(
                task_type_id=2,  # Ensure task_type_id=2 exists and is correct
                description=f"ავტომატური შექმნილი დავალება {task.id}",
                created_by=current_user.id,
                parent_task_id=task.id,
                order_id=task.order_id
            )
            db.session.add(new_task)
        if status_id == '3' and task.task_type_id == 2:
            # Create a subtask with necessary fields
            new_task = Tasks(
                task_type_id=4,  # Ensure task_type_id=2 exists and is correct
                description=f"ავტომატური შექმნილი დავალება {task.id}",
                created_by=current_user.id,
                parent_task_id=task.id,
                order_id=task.order_id
            )
            db.session.add(new_task)

        db.session.commit()

        response = {
            'message': 'დავალება წარმატებით განახლდა!',
            'new_status': {
                'id': task.status.id,
                'name_geo': task.status.name_geo,
                'bootstrap_class': task.status.bootstrap_class
            },
            'assigned_user': {
                'id': task.assigned_user.id if task.assigned_user else None,
                'name': task.assigned_user.name if task.assigned_user else 'შემსრულებელი არ არის მითითებული'
            }
        }

        if new_task:
            response['new_task'] = {
                'id': new_task.id,
                'description': new_task.description,
                'status': {
                    'id': new_task.status.id,
                    'name_geo': new_task.status.name_geo,
                    'bootstrap_class': new_task.status.bootstrap_class
                },
                'task_type': {
                    'id': new_task.task_type.id,
                    'name_geo': new_task.task_type.name
                },
                'created_at': new_task.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            response['message'] += ' ქვეჯამაკური წარმატებით შექმნილია!'

        return jsonify(response), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'შეცდომა: {str(e)}'}), 500


@tasks.route('/tasks/<int:task_id>/add_comment', methods=['POST'])
@login_required
def add_comment(task_id):
    """
    Adds a comment to a task.
    """
    task = Tasks.query.get_or_404(task_id)
    data = request.get_json()
    content = data.get('content', '').strip()

    if not content:
        return jsonify({'message': 'კომენტარი არ უნდა იყოს ცარიელი.'}), 400

    try:
        comment = TaskComments(task_id=task_id, user_id=current_user.id, content=content)
        db.session.add(comment)
        # Update comments_count
        task.comments_count += 1
        db.session.commit()

        response = {
            'message': 'კომენტარი წარმატებით დამატებულია.',
            'comment': {
                'id': comment.id,
                'user': current_user.name,  # Ensure Users model has a name field
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

    # Set form choices
    form.task_type_id.choices = [(t.id, t.name) for t in TaskTypes.query.all()]
    form.status_id.choices = [(s.id, s.name_geo) for s in TaskStatuses.query.all()]  # Use name_geo
    form.task_priority_id.choices = [(p.id, p.level_geo) for p in
                                     TaskPriorities.query.all()]  # Assuming there is level_geo
    form.assigned_to.choices = [(u.id, u.name) for u in Users.query.all()]
    form.completed_by.choices = [(u.id, u.name) for u in Users.query.all()]

    # Make fields read-only
    form.task_category_id.render_kw = {'readonly': True, 'disabled': True}
    form.task_type_id.render_kw = {'readonly': True, 'disabled': True}
    form.description.render_kw = {'readonly': True, 'disabled': True}
    form.created_by.render_kw = {'readonly': True, 'disabled': True}
    form.completed_by.render_kw = {'readonly': True, 'disabled': True}

    # Get comments ordered by date
    comments = task.comments.order_by(TaskComments.timestamp.asc()).all()

    # Get subtasks ordered by creation date
    subtasks = task.subtasks.order_by(Tasks.created_at.asc()).all()

    # Get statuses and users to pass to template
    statuses = TaskStatuses.query.all()
    users = Users.query.all()
    priorities = TaskPriorities.query.all()

    return render_template(
        'tasks/view_task.html',
        form=form,
        task=task,
        comments=comments,
        subtasks=subtasks,  # Added
        statuses=statuses,  # Added
        users=users,  # Added
        priorities=priorities  # Added, if used
    )


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


# ------------- Page and API for tasks list ---------------

@tasks.route('/tasks/list', methods=['GET'])
@login_required
def tasks_list():
    """
    Displays the tasks list page with filtering and pagination.
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
    categories = TaskTypes.query.all()  # Using TaskTypes as categories
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
    Filters are taken from GET parameters, as in the tasks list route.
    """
    # Get filtering parameters from GET request
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
    from ..forms.tasks import TaskForm  # Import form
    form = TaskForm()

    # If no categories yet, pass an empty list
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
                return jsonify({'message': 'MAC-მისამართი აუცილებელია ამ სტატუსისა და ტიპის დავალებისთვის.'}), 400
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
                    'name_geo': subtask.status.name_geo,
                    'bootstrap_class': subtask.status.bootstrap_class
                },
                'task_type': {
                    'id': subtask.task_type.id,
                    'name_geo': subtask.task_type.name_geo
                },
                'created_user': {
                    'name': subtask.created_user.name if subtask.created_user else 'უცნობი'
                },
                'created_at': subtask.created_at.strftime('%Y-%m-%d %H:%M:%S')
            },
            'new_status': {
                'id': parent_task.status_id,
                'name_geo': parent_task.status.name_geo,
                'bootstrap_class': parent_task.status.bootstrap_class
            },
            'customer_account': None
        }
        return jsonify(response), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'შეცდომა: {str(e)}'}), 500


@tasks.route('/tasks/design_tasks_orders', methods=['GET'])
@login_required
def design_tasks_orders():
    """
    Отображает страницу списка задач с использованием пользовательского SQL-запроса.
    """
    # Предполагается, что у вас есть модели TaskType и TaskStatus
    task_types = TaskTypes.query.all()
    task_statuses = TaskStatuses.query.all()
    return render_template(
        'tasks/design_tasks_orders.html',
        task_types=task_types,
        task_statuses=task_statuses,
        active_menu='project_design'

    )


@tasks.route('/api/design_tasks_orders_list', methods=['GET'])
@login_required
def api_design_tasks_orders_list():
    """
    Возвращает данные задач и заказов в формате JSON для отображения в таблице.
    Поддерживает фильтрацию и пагинацию.
    """
    # Получение параметров фильтрации из запроса
    search = request.args.get('search', '', type=str)
    task_type_id = request.args.get('task_type_id', type=int)
    status_id = request.args.get('status_id', type=int)
    customer_name = request.args.get('customer_name', '', type=str)
    order_id = request.args.get('order_id', type=int)
    per_page = request.args.get('per_page', 10, type=int)
    page = request.args.get('page', 1, type=int)

    # Базовый SQL-запрос без жёстких фильтров
    sql = """
    SELECT t.id         as taskID,
           tt.id        as taskTypeID,
           s.id         as taskStatusID,
           s.name_geo   as taskStatusName,
           tt.name      as taskTypeName,
           o.id         as orderID,
           c.id         as customerID,
           c.name       as customerName,
           ct.id        as customerTypeID,
           ct.name      as customerTypeName,
           o.mobile     as mobile,
           o.alt_mobile as alt_mobile,
           tp.id        as tariffPlanID,
           tp.name      as tariffPlanName,
           st.id        as settlementID,
           st.name      as settlementName,
           dt.id        as district,
           dt.name      as districtName
    FROM tasks t
             INNER JOIN task_statuses s ON t.status_id = s.id
             INNER JOIN orders o ON t.order_id = o.id
             INNER JOIN task_types tt ON t.task_type_id = tt.id
             INNER JOIN divisions d ON tt.division_id = d.id
             INNER JOIN customers c ON o.customer_id = c.id
             INNER JOIN customers_type ct ON c.type_id = ct.id
             INNER JOIN tariff_plans tp ON o.tariff_plan_id = tp.id
             INNER JOIN addresses a ON o.address_id = a.id
             INNER JOIN settlements st ON a.settlement_id = st.id
             INNER JOIN districts dt ON st.district_id = dt.id
             INNER JOIN regions r ON dt.region_id = r.id
             INNER JOIN building_types bt ON a.building_type_id = bt.id
    WHERE t.task_type_id = 1
      AND t.status_id = 1
    """

    # Добавление условий фильтрации
    params = {}

    if status_id:
        sql += " AND t.status_id = :status_id"
        params['status_id'] = status_id
    if search:
        sql += f" AND (c.name LIKE '%{search}%' OR o.mobile LIKE '%{search}%')"
        params['search'] = f"%{search}%"

    # Добавление сортировки и пагинации
    sql += " ORDER BY t.id DESC"
    offset = (page - 1) * per_page
    sql += " LIMIT :limit OFFSET :offset"
    params['limit'] = per_page
    params['offset'] = offset

    try:
        # Выполнение SQL-запроса с использованием text()
        result = db.session.execute(db.text(sql), params)
        tasks_orders = result.mappings().all()  # Используем mappings().all()

        # Подсчет общего количества записей для пагинации
        count_sql = """
        SELECT COUNT(*) 
        FROM tasks t
                 INNER JOIN task_statuses s ON t.status_id = s.id
                 INNER JOIN orders o ON t.order_id = o.id
                 INNER JOIN task_types tt ON t.task_type_id = tt.id
                 INNER JOIN divisions d ON tt.division_id = d.id
                 INNER JOIN customers c ON o.customer_id = c.id
                 INNER JOIN customers_type ct ON c.type_id = ct.id
                 INNER JOIN tariff_plans tp ON o.tariff_plan_id = tp.id
                 INNER JOIN addresses a ON o.address_id = a.id
                 INNER JOIN settlements st ON a.settlement_id = st.id
                 INNER JOIN districts dt ON st.district_id = dt.id
                 INNER JOIN regions r ON dt.region_id = r.id
                 INNER JOIN building_types bt ON a.building_type_id = bt.id
        WHERE t.task_type_id = 1
          AND t.status_id = 1
        """
        if status_id:
            count_sql += " AND t.status_id = :status_id"
        if search:
            count_sql += f" AND (c.name LIKE '%{search}%' OR o.mobile LIKE '%{search}%')"

        count_result = db.session.execute(db.text(count_sql), params)
        total = count_result.scalar()

        # Преобразование результатов в список словарей
        tasks_orders_data = [dict(row) for row in tasks_orders]

        # Подготовка данных для ответа
        response = {
            "tasks_orders": tasks_orders_data,
            "pagination": {
                "total": total,
                "per_page": per_page,
                "current_page": page,
                "pages": (total + per_page - 1) // per_page,
                "has_prev": page > 1,
                "has_next": page < (total + per_page - 1) // per_page
            }
        }

    except Exception as e:
        return jsonify({"tasks_orders": [], "pagination": {}}), 500

    return jsonify(response)


@tasks.route('/tasks/export_design_tasks_orders', methods=['GET'])
@login_required
def export_design_tasks_orders():
    """
    Экспортирует фильтрованные данные задач и заказов в файл Excel.
    """
    # Получение параметров фильтрации из запроса
    search = request.args.get('search', '', type=str)
    task_type_id = request.args.get('task_type_id', type=int)
    status_id = request.args.get('status_id', type=int)
    customer_name = request.args.get('customer_name', '', type=str)
    order_id = request.args.get('order_id', type=int)

    # Базовый SQL-запрос
    sql = """
    SELECT t.id         as taskID,
           tt.id        as taskTypeID,
           s.id         as taskStatusID,
           s.name_geo   as taskStatusName,
           tt.name      as taskTypeName,
           o.id         as orderID,
           c.id         as customerID,
           c.name       as customerName,
           ct.id        as customerTypeID,
           ct.name      as customerTypeName,
           o.mobile     as mobile,
           o.alt_mobile as alt_mobile,
           tp.id        as tariffPlanID,
           tp.name      as tariffPlanName,
           st.id        as settlementID,
           st.name      as settlementName,
           dt.id        as district,
           dt.name      as districtName
    FROM tasks t
             INNER JOIN task_statuses s ON t.status_id = s.id
             INNER JOIN orders o ON t.order_id = o.id
             INNER JOIN task_types tt ON t.task_type_id = tt.id
             INNER JOIN divisions d ON tt.division_id = d.id
             INNER JOIN customers c ON o.customer_id = c.id
             INNER JOIN customers_type ct ON c.type_id = ct.id
             INNER JOIN tariff_plans tp ON o.tariff_plan_id = tp.id
             INNER JOIN addresses a ON o.address_id = a.id
             INNER JOIN settlements st ON a.settlement_id = st.id
             INNER JOIN districts dt ON st.district_id = dt.id
             INNER JOIN regions r ON dt.region_id = r.id
             INNER JOIN building_types bt ON a.building_type_id = bt.id
    WHERE 1=1
    """

    # Добавление условий фильтрации
    params = {}
    if task_type_id:
        sql += " AND t.task_type_id = :task_type_id"
        params['task_type_id'] = task_type_id
    if status_id:
        sql += " AND t.status_id = :status_id"
        params['status_id'] = status_id
    if search:
        sql += " AND (c.name ILIKE :search OR o.mobile ILIKE :search)"
        params['search'] = f"%{search}%"
    if customer_name:
        sql += " AND c.name ILIKE :customer_name"
        params['customer_name'] = f"%{customer_name}%"
    if order_id:
        sql += " AND o.id = :order_id"
        params['order_id'] = order_id

    try:
        # Выполнение SQL-запроса
        result = db.session.execute(db.text(sql), params)
        tasks_orders = result.fetchall()

        # Преобразование результатов в DataFrame
        tasks_orders_data = [dict(row) for row in tasks_orders]
        df = pd.DataFrame(tasks_orders_data)

        # Если DataFrame пустой, создаем пустую таблицу
        if df.empty:
            df = pd.DataFrame(columns=[
                'ID დავალება', 'ID ტიპი', 'ID სტატუსი', 'სტატუსის სახელი', 'ტიპის სახელი',
                'ID შეკვეთა', 'ID მომხმარებელი', 'სახელი მომხმარებელი', 'ID მომხმარებლის ტიპი',
                'სახელი მომხმარებლის ტიპი', 'მობილური', 'სანამობილური', 'ID ტარიფი',
                'ტარიფის სახელი', 'ID დასახლებულობა', 'დასახლებულობა', 'ID რაიონი',
                'რაიონის სახელი'
            ])

        # Создание Excel файла
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Tasks_Orders')
        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name='tasks_orders_list.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        return jsonify({"message": "Ошибка при экспорте данных."}), 500
