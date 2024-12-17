from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, Response
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from ..models import TaskTypes, Divisions, Departments
from ..extensions import db
from ..forms.task_types import TaskTypeForm

import datetime
from io import BytesIO

task_types = Blueprint('task_types', __name__)

import pandas as pd
from flask import Response


# Function: Export task types to Excel
@task_types.route('/tasks/task_types/export_task_types_to_excel', methods=['GET'])
@login_required
def export_task_types_to_excel(query):
    """
    Exports the task types data to an Excel file based on the provided query.
    """
    # Retrieve data for export
    task_types = query.all()
    data = [{
        'ID': task_type.id,
        'დავალების ტიპი': task_type.name,
        'დეპარტამენტი': task_type.division.department.name,
        'განხოფილება': task_type.division.name
    } for task_type in task_types]

    # Convert data to a pandas DataFrame
    df = pd.DataFrame(data)

    # Write the DataFrame to a BytesIO stream for Excel export
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='დავალების ტიპები')

    output.seek(0)  # Reset pointer to the start of the stream

    # Return the Excel file as a response
    response = Response(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response.headers["Content-Disposition"] = f"attachment; filename=task_types_report_{datetime.datetime.now()}.xlsx"
    return response


# Route: List of task types
@task_types.route('/tasks/task_types/list', methods=['GET'])
@login_required
def list():
    """
    Displays a paginated and filterable list of task types.
    Supports filtering by department, division, and search query, and allows exporting to Excel.
    """
    # Permission check
    if 'task_types_list' not in [perm['name'] for perm in current_user.get_permissions(current_user.id)]:
        flash("წვდომა აკრცალებელია. საციროა ნებართვა: 'task_types_list'", 'danger')
        return redirect(url_for('dashboard.index'))

    # Retrieve filter parameters
    search_query = request.args.get('search', '')
    department_id = request.args.get('department_id', type=int)
    division_id = request.args.get('division_id', type=int)
    export = request.args.get('export', 'false')  # Flag for Excel export
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Base query with filtering logic
    query = TaskTypes.query.join(Divisions).join(Departments).filter(
        or_(
            TaskTypes.name.ilike(f'%{search_query}%'),
            Divisions.name.ilike(f'%{search_query}%'),
            Departments.name.ilike(f'%{search_query}%')
        )
    )

    # Apply filters for department and division
    if department_id:
        query = query.filter(Departments.id == department_id)
    if division_id:
        query = query.filter(Divisions.id == division_id)

    # Export filtered data to Excel if 'export' flag is true
    if export == 'true':
        return export_task_types_to_excel(query)

    # Pagination
    total_count = query.count()
    offset = (page - 1) * per_page
    task_types = query.limit(per_page).offset(offset).all()

    # Simple pagination class
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

    # Fetch departments and divisions for filters
    departments = Departments.query.all()
    divisions = Divisions.query.filter_by(department_id=department_id).all() if department_id else []

    return render_template('task_types/list.html',
                           task_types=task_types,
                           pagination=pagination,
                           departments=departments,
                           divisions=divisions,
                           department_id=department_id,
                           division_id=division_id,
                           search_query=search_query,
                           active_menu='tasks')


# Route: Create a new task type
@task_types.route('/tasks/task_types/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Allows the user to create a new task type.
    Checks for the required permission before rendering the form.
    """
    if 'task_types_create' not in [perm['name'] for perm in current_user.get_permissions(current_user.id)]:
        flash("წვდომა აკრძალულია. საჭიროა ნებართვა: 'task_types_create'", 'danger')
        return redirect(url_for('task_types.list'))

    form = TaskTypeForm()
    form.department_id.choices = [(d.id, d.name) for d in Departments.query.all()]

    if request.method == 'POST':
        if form.department_id.data:
            form.division_id.choices = [(d.id, d.name) for d in
                                        Divisions.query.filter_by(department_id=form.department_id.data).all()]

        if form.validate_on_submit():
            try:
                # Save new task type to the database
                task_type = TaskTypes(
                    name=form.name.data,
                    division_id=form.division_id.data
                )
                db.session.add(task_type)
                db.session.commit()
                flash('დავალების ტიპი წარმატებით შეიქმნა!', 'success')
                return redirect(url_for('task_types.list'))
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f"ბაზის შეცდომა: {str(e)}", 'danger')
        else:
            flash("გთხოვთ, შეავსოთ ყველა ველი სწორად.", 'danger')

    divisions = Divisions.query.filter_by(
        department_id=form.department_id.data).all() if form.department_id.data else []
    return render_template('task_types/create.html', form=form, departments=Departments.query.all(),
                           divisions=divisions)


# Route: Edit an existing task type
@task_types.route('/tasks/task_types/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """
    Allows the user to edit an existing task type.
    Checks for the required permission and validates input before updating the database.
    """
    if 'task_types_edit' not in [perm['name'] for perm in current_user.get_permissions(current_user.id)]:
        flash("წვდომა აკრძალულია. საჭიროა ნებართვა: 'task_types_edit'", 'danger')
        return redirect(url_for('task_types.list'))

    task_type = TaskTypes.query.get(id)
    if not task_type:
        flash('დავალების ტიპი ვერ მოიძებნა!', 'danger')
        return redirect(url_for('task_types.list'))

    form = TaskTypeForm(obj=task_type)

    current_division = Divisions.query.get(task_type.division_id)
    current_department_id = current_division.department_id if current_division else None

    if form.validate_on_submit():
        try:
            # Update task type details in the database
            task_type.name = form.name.data
            task_type.division_id = form.division_id.data
            db.session.commit()
            flash('დავალების ტიპი წარმატებით დარედაქტირდა!', 'success')
            return redirect(url_for('task_types.list'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"დაფიქსირდა შეცდომა: {str(e)}", 'danger')

    departments = Departments.query.all()
    divisions = Divisions.query.filter_by(department_id=current_department_id).all() if current_department_id else []

    return render_template('task_types/edit.html',
                           form=form,
                           task_type=task_type,
                           departments=departments,
                           divisions=divisions,
                           current_department_id=current_department_id,
                           active_menu='tasks')


# Route: Fetch divisions for a selected department (AJAX endpoint)
@task_types.route('/tasks/task_types/get_divisions/<int:department_id>', methods=['GET'])
@login_required
def get_divisions(department_id):
    """
    Returns a JSON list of divisions for the given department ID.
    Used for dynamically updating the division dropdown in the form.
    """
    divisions = Divisions.query.filter_by(department_id=department_id).all()
    divisions_list = [{'id': division.id, 'name': division.name} for division in divisions]
    return jsonify({'divisions': divisions_list})
