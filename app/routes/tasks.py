# crm_flask/app/routes/tasks.py
import uuid

from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
import sqlalchemy as sa
from ..extensions import db
from ..models import Tasks, TaskStatuses, TaskPriorities, Users, TaskTypes, Divisions, CustomerAccount
from ..forms import TaskForm
import pandas as pd
from io import BytesIO

tasks = Blueprint('tasks', __name__)

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

    # Gather task types for the current division if it exists
    if task.task_type and task.task_type.division:
        task_types = TaskTypes.query.filter_by(division_id=task.task_type.division_id).all()
    else:
        task_types = TaskTypes.query.all()

    # Check for existing MAC address if there's a related account
    mac_address = ''
    if task.order and task.order.customer_account:
        account = task.order.customer_account
        mac_address = account.mac_address if account.mac_address else ''

    # Return JSON response
    return jsonify({
        'id': task.id,
        # These three lines below are not used in final JSON, but represent placeholders
        # that were in the snippet. We keep the logic consistent but typically wouldn't
        # keep empty placeholders in production. For clarity, they are commented out or replaced.
        #
        # "current_status": {"id": ..., "name": ...},
        # "task_type": {"id": ..., "name": ..., "division": {"id": ..., "name": ...}},
        #
        'description': task.description,
        'created_user': task.created_user.name if task.created_user else 'Unknown',
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
            } if task.task_type and task.task_type.division else {}
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
    Updates task status and checks MAC address logic if required.
    Additionally checks if parent_task_type_id=3 and parent_status_change_id=3 => need MAC.
    """
    task = Tasks.query.get_or_404(task_id)
    data = request.get_json()

    # 1) Получаем из JSON поля "parent_task_type_id" и "parent_status_change_id"
    parent_task_type_id = data.get('parent_task_type_id')
    parent_status_change_id = data.get('parent_status_change_id')

    # 2) Обычные поля
    status_id = data.get('status_id')
    mac_address = data.get('macAddress')

    if status_id:
        try:
            # 3) Если у родителя тип=3 и статус=3, а mac_address пуст => ошибка
            if parent_task_type_id == 3 and parent_status_change_id == 3 and not mac_address:
                return jsonify({
                    'message': 'MAC-მისამართი აუცილებელია ამ სტატუსისა და ტიპის დავალებისთვის (Parent).'
                }), 400

            # 4) Обновляем статус текущей задачи
            task.status_id = parent_status_change_id

            # 5) Если текущая задача (this task) тоже тип=3 и статус=3 => проверяем MAC
            if task.task_type_id == 3 and task.status_id == 3:
                if not mac_address:
                    return jsonify({'message': 'MAC-მისამართი აუცილებელია ამ სტატუსისა და ტიპის დავალებისთვის.'}), 400

                # Проверяем дубли
                duplicate_mac = CustomerAccount.query.filter_by(mac_address=mac_address).first()
                if duplicate_mac:
                    return jsonify({
                        'message': f'MAC-მისამართი უკვე გამოყენებულია payID: ( {duplicate_mac.account_pay_number} ).'
                    }), 400

                # Если всё ок, создаём новый CustomerAccount
                new_account = CustomerAccount(
                    customer_id=task.order.customer_id,
                    mac_address=mac_address,
                    tariff_plan_id=task.order.tariff_plan_id,
                    order_id=task.order.id,
                    device_name='Wi-Fi Router',
                    device_type='Router'
                )
                db.session.add(new_account)

            db.session.commit()
            return jsonify({
                'message': 'სტატუსი წარმატებით განახლდა!',
                'new_status': {
                    'id': task.status_id,
                    'name': task.status.name,
                    'bootstrap_class': task.status.bootstrap_class
                }
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'შეცდომა: {str(e)}'}), 400
    else:
        return jsonify({'message': 'სტატუსი არ არის მითითებული.'}), 400


@tasks.route('/tasks/view/<int:task_id>', methods=['GET', 'POST'])
@login_required
def view_task(task_id):
    """
    Renders a page to view/edit task via WTForms.
    """
    task = Tasks.query.get_or_404(task_id)
    form = TaskForm(obj=task)

    form.task_type_id.choices = [(type.id, type.name) for type in TaskTypes.query.all()]
    form.status_id.choices = [(status.id, status.name) for status in TaskStatuses.query.all()]
    form.task_priority_id.choices = [(priority.id, priority.level) for priority in TaskPriorities.query.all()]
    form.assigned_to.choices = [(user.id, user.name) for user in Users.query.all()]
    form.completed_by.choices = [(user.id, user.name) for user in Users.query.all()]

    # Make some fields read-only or disabled
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
            flash("დავალება წარმატებით განახლდა!", "success")  # user sees Georgian message
            return redirect(url_for('tasks.tasks_list'))
        except Exception as e:
            db.session.rollback()
            flash(f"შეცდომა დავალების განახლებაში: {str(e)}", "danger")  # user sees Georgian message

    return render_template(
        'tasks/view_task.html',
        form=form,
        task=task
    )


@tasks.route('/tasks/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """
    Example of editing a task using another WTForms approach.
    """
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
            flash("დავალება წარმატებით განახლდა!", "success")  # user sees Georgian message
            return redirect(url_for('tasks.tasks_list'))
        except Exception as e:
            db.session.rollback()
            flash(f"შეცდომა რედაქტირებისას: {str(e)}", "danger")  # user sees Georgian message

    return render_template('tasks/edit_task.html', form=form, task=task)


@tasks.route('/tasks/list', methods=['GET'])
@login_required
def tasks_list():
    """
    Implements filtering and pagination for the tasks list.
    """
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

    tasks_list_paginated = query.paginate(page=page, per_page=per_page)
    statuses = TaskStatuses.query.all()
    priorities = TaskPriorities.query.all()
    users = Users.query.all()

    return render_template(
        'tasks/task_list.html',
        tasks=tasks_list_paginated.items,
        pagination=tasks_list_paginated,
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
    """
    Exports task data to an Excel file.
    """
    tasks_query = Tasks.query.all()
    task_data = [{
        'ID': task.id,
        'Описание': task.description,
        'Статус': task.status.name if task.status else '',
        'Приоритет': task.priority.name if task.priority else '',
        'Дата создания': task.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for task in tasks_query]

    df = pd.DataFrame(task_data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Tasks')

    output.seek(0)
    return send_file(output, as_attachment=True, download_name='tasks_list.xlsx')


@tasks.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    """
    Renders a page to create a new task (using WTForms).
    """
    from ..forms.tasks import TaskForm
    form = TaskForm()

    # Suppose we have a list of categories (empty for example):
    categories = []

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
            flash("დავალება წარმატებით შეიქმნა!", "success")  # user sees Georgian message
            return redirect(url_for('tasks.tasks_list'))
        except Exception as e:
            db.session.rollback()
            flash(f"შეცდომა დავალების შექმნისას: {str(e)}", "danger")  # user sees Georgian message

    return render_template('tasks/create_task.html', form=form)


@tasks.route('/tasks/create_subtask', methods=['POST'])
@login_required
def create_subtask():
    """
    Creates a subtask if status=3 and task_type=3, checks MAC address.
    """
    data = request.get_json()
    parent_task_id = data.get('parent_task_id')
    description = data.get('description')
    status_id = data.get('status_id')
    task_type_id = data.get('task_type_id')
    order_id = data.get('order_id')
    mac_address = data.get('mac_address')

    parent_task_type_id = data.get('parent_task_type_id')
    parent_status_change_id = data.get('parent_status_change_id')

    parent_task = Tasks.query.get(parent_task_id)
    if not parent_task:
        return jsonify({'message': 'მთავარი დავალება ვერ მოიძებნა.'}), 404

    try:
        # If we create a subtask with type=3 and status=3, we must check MAC
        if int(parent_task_type_id) == 3 and parent_status_change_id == 3:
            if not mac_address:
                return jsonify({'message': 'MAC-მისამართი აუცილებელია ამ სტატუსისა და ტიპის დავალებისთვის.'}), 400
            duplicate_mac = CustomerAccount.query.filter_by(mac_address=mac_address).first()
            if duplicate_mac:
                return jsonify({'message': 'MAC-მისამართი უკვე გამოყენებულია.', 'field': 'mac_address'}), 400

        # Create a new subtask
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
                    } if subtask.task_type.division else {}
                },
                'created_user': {
                    'name': subtask.created_user.name if subtask.created_user else 'Unknown'
                },
                'created_at': subtask.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }

        return jsonify(response), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'შეცდომა: {str(e)}'}), 500
