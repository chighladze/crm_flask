# crm_flask/app/routes/customers.py
from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
import sqlalchemy as sa
from ..extensions import db
from ..forms.customers import CustomerForm
from ..forms.orders import OrderForm
from ..models import Customers, CustomersType, Addresses, Orders, Coordinates
from sqlalchemy.exc import SQLAlchemyError
from io import BytesIO
import pandas as pd

customers = Blueprint('customers', __name__)

@customers.route('/customers/create', methods=['GET', 'POST'])
@login_required
def create():
    # Check permissions
    if 'customer_create' not in [perm['name'] for perm in current_user.get_permissions(current_user.id)]:
        flash("Access denied. Permission required: 'customer_create'", 'danger')
        return redirect(url_for('dashboard.index'))

    # Initialize forms
    customer_form = CustomerForm()
    order_form = OrderForm()
    create_with_order = request.form.get('create_order', 'false') == 'true'

    is_customer_form_valid = customer_form.validate_on_submit()
    is_order_form_valid = order_form.validate_on_submit() if create_with_order else True

    if is_customer_form_valid and is_order_form_valid:
        try:
            # Create and save customer
            customer = Customers(
                type_id=customer_form.type_id.data,
                identification_number=customer_form.identification_number.data,
                name=customer_form.name.data,
                email=customer_form.email.data,
                mobile=customer_form.mobile.data,
                mobile_second=customer_form.mobile_second.data,
                resident=int(customer_form.resident.data) if customer_form.resident.data else 1
            )
            db.session.add(customer)
            db.session.commit()

            # Set customer_id in order_form
            if create_with_order:
                order_form.customer_id.data = customer.id  # Set customer_id

                # Create coordinates only if latitude and longitude are provided
                latitude = order_form.address.latitude.data
                longitude = order_form.address.longitude.data
                coordinates = None
                if latitude is not None and longitude is not None:
                    coordinates = Coordinates(
                        latitude=latitude,
                        longitude=longitude,
                    )
                    db.session.add(coordinates)
                    db.session.commit()

                # Create and save address
                address = Addresses(
                    settlement_id=order_form.address.settlement_id.data,
                    building_type_id=order_form.address.building_type_id.data,
                    street=order_form.address.street.data,
                    building_number=order_form.address.building_number.data,
                    entrance_number=order_form.address.entrance_number.data,
                    floor_number=order_form.address.floor_number.data,
                    apartment_number=order_form.address.apartment_number.data,
                    coordinates_id=coordinates.id if coordinates else None,
                    registry_code=order_form.address.registry_code.data,
                )
                db.session.add(address)
                db.session.commit()

                # Create and save order linked to customer and address
                order = Orders(
                    customer_id=order_form.customer_id.data,  # Use customer_id from order_form
                    address_id=address.id,
                    mobile=order_form.mobile.data,
                    alt_mobile=order_form.alt_mobile.data,
                    tariff_plan_id=order_form.tariff_plan_id.data,
                    comment=order_form.comment.data,
                )
                db.session.add(order)
                db.session.commit()

                flash('Client and order created successfully!', 'success')
            else:
                flash('Client created successfully!', 'success')

            return redirect(url_for('customers.view', id=customer.id))

        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", 'danger')
    else:
        if not is_customer_form_valid:
            for field, errors in customer_form.errors.items():
                for error in errors:
                    flash(f"{field}: {error}", 'danger')
        if create_with_order and not is_order_form_valid:
            for field, errors in order_form.errors.items():
                for error in errors:
                    flash(f"{field}: {error}", 'danger')

    # Render form
    return render_template(
        'customers/create.html',
        customer_form=customer_form,
        order_form=order_form,
        create_with_order=create_with_order,
        active_menu='customers'
    )



@customers.route('/customer/<int:id>/view', methods=['GET'])
@login_required
def view(id):
    customer = Customers.query.get_or_404(id)
    orders = Orders.query.filter_by(customer_id=customer.id).all()  # Получаем заказы клиента
    customer.orders = orders  # Добавляем заказы к объекту клиента
    return render_template('customers/view.html', customer=customer, active_menu='customers')


@customers.route('/customers/list', methods=['GET', 'POST'])
@login_required
def customers_list():
    if 'customers_list' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash("თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['customers_list']", 'danger')
        return redirect(url_for('dashboard.index'))

    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    type_id = request.args.get('type_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    sort_by = request.args.get('sort_by', 'created_desc')

    # Ограничение допустимых значений для per_page
    per_page = per_page if per_page in [10, 50, 100] else 10

    # Начало построения запроса
    query = Customers.query.filter(
        sa.or_(
            Customers.name.ilike(f'%{search_query}%'),
            Customers.identification_number.ilike(f'%{search_query}%')
        )
    )

    # Применение фильтров
    if type_id:
        query = query.filter(Customers.type_id == type_id)
    if start_date:
        query = query.filter(Customers.created_at >= start_date)
    if end_date:
        query = query.filter(Customers.created_at <= end_date)

    # Применение сортировки
    if sort_by == 'created_asc':
        query = query.order_by(Customers.created_at.asc())
    else:
        query = query.order_by(Customers.created_at.desc())

    # Получение общего количества клиентов
    total_count = query.count()

    # Пагинация
    offset = (page - 1) * per_page
    customers = query.limit(per_page).offset(offset).all()

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
        sort_by=sort_by,
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


@customers.route('/customers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if 'customer_edit' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash("You do not have access to this page. Permission required: ['customer_edit']", 'danger')
        return redirect(url_for('dashboard.index'))

    customer = Customers.query.filter_by(id=id).first_or_404()

    form = CustomerForm(obj=customer)
    if form.validate_on_submit():
        form.populate_obj(customer)  # Обновляем данные клиента из формы
        db.session.commit()
        flash('კლიენტის მონაცემები განახლებულია!', 'success')
        return redirect(url_for('customers.view', id=customer.id))

    return render_template('customers/edit.html', form=form, customer=customer, active_menu='customers')


@customers.route('/customers/check_identification', methods=['POST'])
@login_required
def check_identification():
    identification_number = request.json.get('identification_number')

    if identification_number:
        customer = Customers.query.filter_by(identification_number=identification_number).first()
        if customer:
            return jsonify({
                'exists': True,
                'name': customer.name,
                'id': customer.id
            }), 200
    return jsonify({'exists': False}), 200
