from datetime import datetime

from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
import sqlalchemy as sa
from ..extensions import db
from ..forms.customers import CustomerForm
from ..models.customers import Customers
from ..models.customer_type import CustomersType
from io import BytesIO
import pandas as pd

customers = Blueprint('customers', __name__)


@customers.route('/customers/create', methods=['GET', 'POST'])
@login_required
def create():
    if 'customer_create' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash("თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['customer_create']", 'danger')
        return redirect(url_for('dashboard.index'))

    form = CustomerForm()

    if form.validate_on_submit():
        customer = Customers(
            type_id=form.type_id.data,
            identification_number=form.identification_number.data,
            name=form.name.data,
            email=form.email.data,
            mobile=form.mobile.data,
            mobile_second=form.mobile_second.data
        )
        db.session.add(customer)
        db.session.commit()
        flash('კლინეტი წარმატებით დამატებულია!', 'success')

        # Redirect to the newly created customer's detail page
        return redirect(url_for('customers.view', id=customer.id))  # Используем id для редиректа

    return render_template('customers/create.html', form=form, active_menu='customers')


@customers.route('/customer/<int:id>/view', methods=['GET'])
@login_required
def view(id):
    customer = Customers.query.get_or_404(id)
    return render_template('customers/view.html', customer=customer)


@customers.route('/check_customer_id', methods=['POST'])
def check_customer_id():
    data = request.get_json()
    id_number = data.get('id_number')

    if not id_number:
        return jsonify({"exists": False})

    customer = Customers.query.filter_by(identification_number=id_number).first()

    if customer:
        # Get the name of the client type
        customer_type = CustomersType.query.filter_by(id=customer.type_id).first()
        type_name = customer_type.name if customer_type else "Unknown"  # Или любое другое значение по умолчанию

        return jsonify({
            "exists": True,
            "customer": {
                "id": customer.id,
                "type_id": customer.type_id,
                "type_name": type_name,  # Adding a client type name
                "email": customer.email,
                "mobile": customer.mobile,
                "mobile_second": customer.mobile_second,
                "identification_number": customer.identification_number,
                "name": customer.name
            }
        })
    else:
        return jsonify({"exists": False})


@customers.route('/customers/list', methods=['GET', 'POST'])
@login_required
def customers_list():
    if 'customers_list' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash("თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['customers_list']", 'danger')
        return redirect(url_for('dashboard.index'))

    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)  # Номер страницы
    per_page = request.args.get('per_page', 10, type=int)  # Число записей на странице, по умолчанию 10
    type_id = request.args.get('type_id', type=int)  # Фильтр по типу клиента
    start_date = request.args.get('start_date')  # Дата начала фильтрации
    end_date = request.args.get('end_date')  # Дата окончания фильтрации

    # Ограничение допустимых значений для per_page
    per_page = per_page if per_page in [10, 50, 100] else 10

    # Начало построения запроса
    query = sa.select(Customers).filter(
        sa.or_(
            Customers.name.ilike(f'%{search_query}%'),
            Customers.identification_number.ilike(f'%{search_query}%')
        )
    )

    # Применение дополнительных фильтров
    if type_id:
        query = query.filter(Customers.type_id == type_id)

    # Преобразование формата дат (если это необходимо)
    if start_date:
        query = query.filter(Customers.created_at >= start_date)
    if end_date:
        query = query.filter(Customers.created_at <= end_date)

    query = query.order_by(Customers.created_at.desc())

    # Получение общего количества клиентов
    total_count = db.session.execute(sa.select(sa.func.count()).select_from(query)).scalar()

    # Пагинация
    offset = (page - 1) * per_page
    paginated_query = query.limit(per_page).offset(offset)
    customers_query = db.session.execute(paginated_query)
    customers = customers_query.scalars().all()

    # Создание объекта пагинации
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

    # Получение типов клиентов для выпадающего списка фильтра
    customer_types = db.session.execute(sa.select(CustomersType)).scalars().all()
    print(customer_types)

    return render_template(
        'customers/customer_list.html',
        customers=customers,
        active_menu='customers',
        pagination=pagination,
        per_page=per_page,
        search_query=search_query,
        start_date=start_date,
        end_date=end_date,
        type_id=type_id,
        customer_types=customer_types
    )


@customers.route('/customers/export', methods=['GET'])
@login_required
def customers_export():
    # Check if the user has permission to export customers
    if 'customers_export' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash("You do not have access to this page. Permission required: ['customers_export']", 'danger')
        return redirect(url_for('dashboard.index'))

    # Получаем параметры фильтрации
    search_query = request.args.get('search', '')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    type_id = request.args.get('type_id')

    # Начинаем формировать запрос
    query = sa.select(Customers)

    # Применяем фильтры по поисковому запросу
    if search_query:
        query = query.filter(
            sa.or_(
                Customers.name.ilike(f'%{search_query}%'),
                Customers.identification_number.ilike(f'%{search_query}%')
            )
        )

    # Применяем фильтры по типу клиента
    if type_id and type_id != '':
        query = query.filter(Customers.type_id == type_id)

    # Применяем фильтры по датам
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(Customers.created_at >= start_date)

    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        query = query.filter(Customers.created_at <= end_date)

    # Выполняем запрос
    customers_query = db.session.execute(query)
    customers = customers_query.scalars().all()

    # Convert customer data into a list of dictionaries
    customer_data = [{
        "ID": customer.id,
        "Type": customer.customer_type.name,
        "Identification Number": customer.identification_number,
        "Name": customer.name,
        "Email": customer.email,
        "Mobile": customer.mobile,
        "Second Mobile": customer.mobile_second,
        "Created At": customer.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        "Updated At": customer.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    } for customer in customers]

    # Create a DataFrame from the customer data
    df = pd.DataFrame(customer_data)

    # Create an Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Customers')

        # Access the active sheet
        worksheet = writer.sheets['Customers']

        # Adjust column width based on the maximum length of content in each column
        for col in worksheet.columns:
            max_length = 0
            column = col[0].column_letter  # Get the letter designation of the column

            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))

            adjusted_width = max_length + 2  # Add some space
            worksheet.column_dimensions[column].width = adjusted_width

    # Move the stream pointer to the beginning of the file
    output.seek(0)

    # Send the file as an attachment
    return send_file(output, as_attachment=True, download_name="customers_list.xlsx",
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


# @customers.route('/customers/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
# def edit(id):
#     if 'customer_edit' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
#         flash('Access denied.', 'danger')
#         return redirect(url_for('dashboard.index'))
#
#     customer = db.session.execute(sa.select(Customers).filter_by(id=id)).scalar_one_or_none()
#     if customer is None:
#         flash('Customer not found!', 'danger')
#         return redirect(url_for('customers.customer_list'))
#
#     form = CustomerForm(obj=customer)
#     if form.validate_on_submit():
#         customer.type_id = form.type_id.data
#         customer.identification_number = form.identification_number.data
#         customer.name = form.name.data
#         customer.email = form.email.data
#         customer.mobile = form.mobile.data
#         customer.mobile_second = form.mobile_second.data
#         db.session.commit()
#         flash('Customer successfully updated!', 'success')
#         return redirect(url_for('customers.customer_list'))
#
#     return render_template('customers/edit.html', form=form, customer=customer, active_menu='customers')
