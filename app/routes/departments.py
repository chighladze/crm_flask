from flask import Blueprint, request, render_template, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
import sqlalchemy as sa
import pandas as pd
from io import BytesIO
from ..extensions import db
from ..forms.departments import DepartmentCreateForm
from ..models.departments import Departments

departments = Blueprint('departments', __name__)


@departments.route('/departments/dep_list', methods=['GET', 'POST'])
@login_required
def dep_list():
    if 'departments_list' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['departments_list']", 'danger')
        return redirect(url_for('dashboard.index'))
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)  # Номер страницы
    per_page = request.args.get('per_page', 10, type=int)  # Количество записей на странице, по умолчанию 10

    # Ограничение допустимых значений для per_page
    per_page = per_page if per_page in [10, 50, 100] else 10

    # Составляем запрос для поиска департаментов
    query = sa.select(Departments).filter(
        sa.or_(
            Departments.name.ilike(f'%{search_query}%')
        )
    ).order_by(Departments.createdAt.desc())  # Добавляем сортировку по дате создания

    # Получаем общее количество департаментов
    total_count_query = sa.select(sa.func.count()).select_from(
        sa.select(Departments).filter(
            sa.or_(
                Departments.name.ilike(f'%{search_query}%')
            )
        )
    )
    total_count = db.session.execute(total_count_query).scalar()

    # Пагинация
    offset = (page - 1) * per_page
    paginated_query = query.limit(per_page).offset(offset)

    # Выполняем запрос с учетом пагинации
    departments_query = db.session.execute(paginated_query)
    departments_list = departments_query.scalars().all()

    # Создаем объект пагинации вручную
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
        'departments/dep_list.html',
        departments=departments_list,  # Переименовали переменную
        active_menu='administration',
        pagination=pagination,
        per_page=per_page
    )


@departments.route('/departments/create', methods=['GET', 'POST'])
@login_required
def create():
    if 'department_create' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['department_create']", 'danger')
        return redirect(url_for('dashboard.index'))
    form = DepartmentCreateForm()
    if form.validate_on_submit():
        department = Departments(name=form.name.data, description=form.description.data)
        db.session.add(department)
        db.session.commit()
        flash('დეპარტამენტი წარმატებით დაემატა!', 'success')
        return redirect(url_for('departments.dep_list'))
    return render_template('departments/create.html', form=form, active_menu='administration')


@departments.route('/departments/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if 'department_edit' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['department_edit']", 'danger')
        return redirect(url_for('dashboard.index'))
    # Retrieve the department to be edited
    department = db.session.execute(sa.select(Departments).filter_by(id=id)).scalar_one_or_none()
    if department is None:
        flash('დეპარტამენტი ვერ მოიძებნა!', 'danger')
        return redirect(url_for('departments.dep_list'))

    # Create a form instance with the current department data
    form = DepartmentCreateForm(obj=department)

    if form.validate_on_submit():
        # Update department details
        department.name = form.name.data
        department.description = form.description.data
        db.session.commit()
        flash('დეპარტამენტი წარმატებით განახლდა!', 'success')
        return redirect(url_for('departments.dep_list'))

    return render_template('departments/edit.html', form=form, department=department, active_menu='administration')


@departments.route('/departments/export', methods=['GET'])
@login_required
def departments_export():
    if 'departments_export' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['departments_export']", 'danger')
        return redirect(url_for('dashboard.index'))
    # Получаем список всех департаментов из базы данных
    departments_query = db.session.execute(sa.select(Departments))
    departments = departments_query.scalars().all()

    # Преобразуем данные в список словарей
    department_data = [{
        "id": department.id,
        "სახელი": department.name,
        "აღწერა": department.description,
        "შექმნის თარიღი": department.createdAt.strftime('%Y-%m-%d %H:%M:%S'),
        "განახლების თარიღი": department.updatedAt.strftime('%Y-%m-%d %H:%M:%S')
    } for department in departments]

    df = pd.DataFrame(department_data)

    # Создаем Excel файл в памяти
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Departments')

        # Доступ к активному листу
        worksheet = writer.sheets['Departments']

        # Автоматически изменяем ширину столбцов
        for col in worksheet.columns:
            max_length = 0
            column = col[0].column_letter  # Получаем буквенное обозначение столбца

            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))

            adjusted_width = max_length + 2  # Добавляем немного пространства
            worksheet.column_dimensions[column].width = adjusted_width

    # Перемещаем указатель потока в начало файла
    output.seek(0)

    # Отправляем файл
    return send_file(output, as_attachment=True, download_name="departments.xlsx",
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
