# crm_flask/app/routes/orders.py
from flask_login import login_required, current_user
from flask import render_template, redirect, url_for, flash, request, jsonify
from app.models import Orders, District, Settlement, BuildingType, Customers, Addresses, TariffPlan, Coordinates, Tasks
from app.forms import OrderForm
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


# crm_flask/app/routes/orders.py
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
            street=form.address.street.data,
            building_number=form.address.building_number.data,
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


@orders.route('/orders/orders_list', methods=['GET', 'POST'])
@login_required
def orders_list():
    # Проверка прав доступа
    if 'orders_list' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash("თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['orders_list']", 'danger')
        return redirect(url_for('dashboard.index'))

    search_query = request.args.get('search', '')
    mobile = request.args.get('mobile', '')
    tariff_plan_id = request.args.get('tariff_plan_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Строим основной запрос с фильтрацией по имени клиента и мобильному телефону
    query = Orders.query.join(Customers).filter(
        sa.or_(
            Orders.mobile.ilike(f'%{search_query}%'),
            Customers.name.ilike(f'%{search_query}%')
        )
    )

    # Фильтрация по мобильному номеру
    if mobile:
        query = query.filter(Orders.mobile.ilike(f'%{mobile}%'))

    # Фильтрация по тарифному плану
    if tariff_plan_id:
        query = query.filter(Orders.tariff_plan_id == tariff_plan_id)

    # Фильтрация по датам
    if start_date:
        query = query.filter(Orders.created_at >= start_date)
    if end_date:
        query = query.filter(Orders.created_at <= end_date)

    # Пагинация
    total_count = query.count()
    offset = (page - 1) * per_page
    orders = query.limit(per_page).offset(offset).all()

    # Пагинация
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

    # Получаем список тарифных планов для фильтрации
    tariff_plans = db.session.query(TariffPlan).all()

    return render_template(
        'orders/order_list.html',
        orders=orders,
        pagination=pagination,
        per_page=per_page,
        search_query=search_query,
        mobile=mobile,
        tariff_plan_id=tariff_plan_id,
        start_date=start_date,
        end_date=end_date,
        tariff_plans=tariff_plans,
        active_menu='orders'
    )


@orders.route('/orders/<int:order_id>/view', methods=['GET'])
@login_required
def order_view(order_id):
    order = Orders.query.options(
        db.joinedload(Orders.address).joinedload(Addresses.coordinates),
        db.joinedload(Orders.task)
    ).get_or_404(order_id)

    # Получить связанные задачи
    related_tasks = Tasks.query.filter(Tasks.parent_task_id == order.task_id).all()

    return render_template(
        'orders/order_view.html',
        order=order,
        related_tasks=related_tasks,
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
        form.address.street.data = address.street
        form.address.building_number.data = address.building_number
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
        address.street = form.address.street.data
        address.building_number = form.address.building_number.data
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
    tariff_plan_id = request.args.get('tariff_plan_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Строим основной запрос с фильтрацией по имени клиента и мобильному телефону
    query = Orders.query.join(Customers).filter(
        sa.or_(
            Orders.mobile.ilike(f'%{search_query}%'),
            Customers.name.ilike(f'%{search_query}%')
        )
    )

    # Фильтрация по мобильному номеру
    if mobile:
        query = query.filter(Orders.mobile.ilike(f'%{mobile}%'))

    # Фильтрация по тарифному плану
    if tariff_plan_id:
        query = query.filter(Orders.tariff_plan_id == tariff_plan_id)

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
        "Mobile": order.mobile,
        "Alt Mobile": order.alt_mobile,
        "Tariff Plan": order.tariff_plan.name if order.tariff_plan else "N/A",
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
