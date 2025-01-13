from flask_login import login_required, current_user
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_wtf.csrf import validate_csrf, ValidationError
from app.models import Orders, District, Settlement, BuildingType, Customers, Addresses, TariffPlan, Coordinates, Tasks, \
    OrderStatus
from app.forms import OrderForm, OrderStatusForm
from flask import Blueprint
from flask import jsonify
import sqlalchemy as sa
from ..extensions import db
import pandas as pd
from io import BytesIO
from flask import send_file

orders = Blueprint('orders', __name__)


@orders.route('/find_customer/<identification_number>', methods=['GET'])
@login_required
def find_customer(identification_number):
    # Поиск клиента по идентификационному номеру
    customer = Customers.query.filter_by(identification_number=identification_number).first()

    if customer:
        # Если клиент найден, возвращаем его данные
        customer_data = {
            'name': customer.name,
            'email': customer.email,
            'mobile': customer.mobile,
            'mobile_second': customer.mobile_second,
            'resident': customer.resident
        }
        return jsonify({'found': True, 'data': customer_data})
    else:
        # Если клиент не найден
        return jsonify({'found': False})


@orders.route('/orders/create', methods=['GET', 'POST'])
@login_required
def create_order():
    form = OrderForm()

    if form.validate_on_submit():
        identification_number = form.identification_number.data

        # Поиск клиента по идентификационному номеру
        customer = Customers.query.filter_by(identification_number=identification_number).first()

        if not customer:
            # Если клиента нет, создаем нового клиента
            customer = Customers(
                type_id=form.type_id.data,
                identification_number=identification_number,
                name=form.name.data,
                email=form.email.data,
                mobile=form.mobile.data,
                mobile_second=form.mobile_second.data,
                resident=form.resident.data
            )
            db.session.add(customer)
            db.session.commit()
            flash('მომხმარებელი წარმატებით დაემატა!', 'success')

        # Создание записи Coordinates, если есть координаты
        latitude = form.address.latitude.data
        longitude = form.address.longitude.data
        coordinates = None
        if latitude and longitude:
            coordinates = Coordinates(latitude=latitude, longitude=longitude)
            db.session.add(coordinates)
            db.session.commit()

        # Создание записи Addresses
        address = Addresses(
            settlement_id=form.address.settlement_id.data,
            building_type_id=form.address.building_type_id.data,
            entrance_number=form.address.entrance_number.data,
            floor_number=form.address.floor_number.data,
            apartment_number=form.address.apartment_number.data,
            coordinates_id=coordinates.id if coordinates else None,
            registry_code=form.address.registry_code.data,
        )
        db.session.add(address)
        db.session.commit()

        # Создание заказа
        order = Orders(
            customer_id=customer.id,
            address_id=address.id,
            mobile=form.mobile.data,
            alt_mobile=form.alt_mobile.data,
            tariff_plan_id=form.tariff_plan_id.data,
            comment=form.comment.data,
            status_id=1,  # Assuming default status
            legal_address=form.legal_address.data,  # Ensure these fields are in the form
            actual_address=form.actual_address.data
        )
        db.session.add(order)
        db.session.commit()

        # Создание задания для установки
        task = Tasks(
            task_category_id=1,
            task_category_type_id=1,
            description=f"შეკვეთის №{order.id}-თვის ახალი დავალება შექმნილია",
            status_id=1,
            task_priority_id=2,
            created_by=current_user.id,
            created_division_id=current_user.division_id if hasattr(current_user, 'division_id') else None,
            order_id=order.id  # Assuming Tasks has order_id field
        )
        db.session.add(task)
        db.session.commit()

        # Обновляем поле task_id в заказе
        order.task_id = task.id
        db.session.commit()

        flash('განაცხადი და დავალება წარმატებით დამატებულია!', 'success')
        return redirect(url_for('customers.view', id=customer.id))

    return render_template('orders/create_order.html', form=form)


@orders.route('/settlements/<int:district_id>')
@login_required
def get_settlements(district_id):
    settlements = Settlement.query.filter_by(district_id=district_id).all()
    return jsonify({'settlements': [{'id': settlement.id, 'name': settlement.name} for settlement in settlements]})


@orders.route('/orders/orders_list', methods=['GET'])
@login_required
def orders_list_page():
    """
    Render the orders list HTML page.
    """
    # Проверка прав доступа
    if 'orders_list' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash("თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['orders_list']", 'danger')
        return redirect(url_for('dashboard.index'))

    # Получаем список тарифных планов для фильтрации
    tariff_plans = TariffPlan.query.all()
    order_statuses = OrderStatus.query.filter_by(hided=False).all()  # New
    districts = District.query.all()  # New
    building_types = BuildingType.query.all()  # New

    return render_template(
        'orders/order_list.html',
        tariff_plans=tariff_plans,
        order_statuses=order_statuses,  # New
        districts=districts,  # New
        building_types=building_types,  # New
        active_menu='orders'
    )


@orders.route('/api/orders_list', methods=['GET'])
@login_required
def api_orders_list():
    """
    API endpoint to get the list of orders based on filters.
    """
    search_query = request.args.get('search', '')
    mobile = request.args.get('mobile', '')
    identification_number = request.args.get('identification_number', '')
    tariff_plan_id = request.args.get('tariff_plan_id', type=int)
    status_id = request.args.get('status_id', type=int)  # New filter
    district_id = request.args.get('district_id', type=int)  # New filter
    building_type_id = request.args.get('building_type_id', type=int)  # New filter
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    page = request.args.get('page', 1, type=int)
    # Get per_page parameter from request; default to 10 if not provided
    per_page = request.args.get('per_page', 10, type=int)

    # Build the query with filters
    query = Orders.query.join(Customers).join(Addresses).join(Settlement).filter(
        sa.or_(
            Orders.mobile.ilike(f'%{search_query}%'),
            Customers.name.ilike(f'%{search_query}%'),
            Customers.identification_number.ilike(f'%{search_query}%')
        )
    )

    if mobile:
        query = query.filter(Orders.mobile.ilike(f'%{mobile}%'))

    if identification_number:
        query = query.filter(Customers.identification_number.ilike(f'%{identification_number}%'))

    if tariff_plan_id:
        query = query.filter(Orders.tariff_plan_id == tariff_plan_id)

    if status_id:
        query = query.filter(Orders.status_id == status_id)

    if district_id:
        query = query.filter(Settlement.district_id == district_id)

    if building_type_id:
        query = query.filter(Addresses.building_type_id == building_type_id)

    if start_date:
        query = query.filter(Orders.created_at >= start_date)

    if end_date:
        query = query.filter(Orders.created_at <= end_date)

    # Apply pagination with the dynamic per_page value
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    orders = pagination.items

    # Serialize orders
    orders_data = [{
        "ID": order.id,
        "Customer": order.customer.name,
        "Identification Number": order.customer.identification_number,
        "Mobile": order.mobile,
        "Alt Mobile": order.alt_mobile,
        "Tariff Plan": order.tariff_plan.name if order.tariff_plan else "N/A",
        "Status": order.status.name_geo if order.status else "N/A",
        "District": order.address.settlement.district.name if order.address.settlement.district else "N/A",
        "Building Type": order.address.building_type.name if order.address.building_type else "N/A",
        "Created At": order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        "Comment": order.comment,
    } for order in orders]

    response = {
        "orders": orders_data,
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


@orders.route('/orders/<int:order_id>/view', methods=['GET'])
@login_required
def order_view(order_id):
    order = Orders.query.options(
        db.joinedload(Orders.address).joinedload(Addresses.coordinates),
        db.joinedload(Orders.task),
        db.joinedload(Orders.customer_account)
    ).get_or_404(order_id)
    all_statuses = OrderStatus.query.filter(OrderStatus.hided == 0).all()

    related_tasks = Tasks.query.filter(Tasks.order_id == order_id).all()

    account = order.customer_account

    return render_template(
        'orders/order_view.html',
        order=order,
        all_statuses=all_statuses,
        related_tasks=related_tasks,
        account=account,
        active_menu='orders'
    )


@orders.route('/orders/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    order = Orders.query.get_or_404(order_id)
    customer = Customers.query.get_or_404(order.customer_id)
    address = Addresses.query.get_or_404(order.address_id)
    coordinates = address.coordinates if address.coordinates_id else None

    form = OrderForm(obj=order)

    # Заполнить подформу адреса
    if address:
        form.address.district_id.data = address.settlement.district_id
        form.address.settlement_id.data = address.settlement_id
        form.address.building_type_id.data = address.building_type_id
        form.address.entrance_number.data = address.entrance_number
        form.address.floor_number.data = address.floor_number
        form.address.apartment_number.data = address.apartment_number
        form.address.registry_code.data = address.registry_code
        if coordinates:
            form.address.latitude.data = coordinates.latitude
            form.address.longitude.data = coordinates.longitude

    if form.validate_on_submit():
        latitude = form.address.latitude.data
        longitude = form.address.longitude.data

        # Обновить или удалить координаты
        if latitude is not None and longitude is not None:
            if not coordinates:
                coordinates = Coordinates()
                db.session.add(coordinates)
            coordinates.latitude = latitude
            coordinates.longitude = longitude
            db.session.commit()
        elif coordinates:
            db.session.delete(coordinates)
            db.session.commit()
            coordinates = None

        # Обновить адрес
        address.settlement_id = form.address.settlement_id.data
        address.building_type_id = form.address.building_type_id.data
        address.entrance_number = form.address.entrance_number.data
        address.floor_number = form.address.floor_number.data
        address.apartment_number = form.address.apartment_number.data
        address.registry_code = form.address.registry_code.data
        address.coordinates_id = coordinates.id if coordinates else None
        db.session.commit()

        # Обновить заказ
        order.mobile = form.mobile.data
        order.alt_mobile = form.alt_mobile.data
        order.tariff_plan_id = form.tariff_plan_id.data
        order.comment = form.comment.data
        order.status_id = form.status_id.data  # Update status if present in form
        order.legal_address = form.legal_address.data
        order.actual_address = form.actual_address.data
        db.session.commit()

        flash('შეკვეთა წარმატებით განახლდა!', 'success')
        return redirect(url_for('orders.order_view', order_id=order.id))

    return render_template(
        'orders/edit_order.html',
        form=form,
        order=order,
        customer=customer
    )


@orders.route('/orders/export', methods=['GET'])
@login_required
def orders_export():
    # Проверка прав доступа
    if 'orders_export' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash("თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['orders_export']", 'danger')
        return redirect(url_for('dashboard.index'))

    search_query = request.args.get('search', '')
    mobile = request.args.get('mobile', '')
    identification_number = request.args.get('identification_number', '')
    tariff_plan_id = request.args.get('tariff_plan_id', type=int)
    status_id = request.args.get('status_id', type=int)  # New filter
    district_id = request.args.get('district_id', type=int)  # New filter
    building_type_id = request.args.get('building_type_id', type=int)  # New filter
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Строим основной запрос с фильтрацией по имени клиента и мобильному телефону
    query = Orders.query.join(Customers).join(Addresses).join(Settlement).filter(
        sa.or_(
            Orders.mobile.ilike(f'%{search_query}%'),
            Customers.name.ilike(f'%{search_query}%')
        )
    )

    # Фильтрация по мобильному номеру
    if mobile:
        query = query.filter(Orders.mobile.ilike(f'%{mobile}%'))

    # Фильтрация по персональному номеру
    if identification_number:
        query = query.filter(Customers.identification_number.ilike(f'%{identification_number}%'))

    # Фильтрация по тарифному плану
    if tariff_plan_id:
        query = query.filter(Orders.tariff_plan_id == tariff_plan_id)

    # Фильтрация по статусу
    if status_id:
        query = query.filter(Orders.status_id == status_id)

    # Фильтрация по району
    if district_id:
        query = query.filter(Settlement.district_id == district_id)

    # Фильтрация по типу здания
    if building_type_id:
        query = query.filter(Addresses.building_type_id == building_type_id)

    # Фильтрация по датам
    if start_date:
        query = query.filter(Orders.created_at >= start_date)
    if end_date:
        query = query.filter(Orders.created_at <= end_date)

    # Получаем все заказы
    orders = query.all()

    # Преобразуем данные в список словарей
    orders_data = [{
        "ID": order.id,
        "Customer": order.customer.name,
        "Identification Number": order.customer.identification_number,
        "Mobile": order.mobile,
        "Alt Mobile": order.alt_mobile,
        "Tariff Plan": order.tariff_plan.name if order.tariff_plan else "N/A",
        "Status": order.status.name if order.status else "N/A",
        "District": order.address.settlement.district.name if order.address.settlement.district else "N/A",
        "Building Type": order.address.building_type.name if order.address.building_type else "N/A",
        "Created At": order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        "Updated At": order.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        "Comment": order.comment,
    } for order in orders]

    # Создаем DataFrame из списка словарей
    df = pd.DataFrame(orders_data)

    # Создаем Excel файл в памяти
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Orders')

        # Настройка ширины столбцов
        worksheet = writer.sheets['Orders']
        for col in worksheet.columns:
            max_length = 0
            column = col[0].column_letter  # Получаем букву колонки
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)  # Добавляем немного места
            worksheet.column_dimensions[column].width = adjusted_width

    # Сбрасываем указатель на начало файла
    output.seek(0)

    # Отправляем файл пользователю
    return send_file(output, as_attachment=True, download_name="orders_list.xlsx",
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@orders.route('/orders/<int:order_id>/update_status', methods=['POST'])
@login_required
def update_order_status(order_id):
    form = OrderStatusForm()
    if form.validate_on_submit():
        try:
            new_status_id = form.new_status.data
            order = Orders.query.get_or_404(order_id)
            order.status_id = new_status_id
            db.session.commit()
            flash('სტატუსი განახლებულია!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('სტატუსის განახლებისას დაფიქსირდა შეცდომა', 'danger')
    else:
        flash('ვალიდაციის შეცდომა.', 'danger')

    return redirect(url_for('orders.order_view', order_id=order_id))
