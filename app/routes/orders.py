# crm_flask/app/routes/orders.py
from flask import render_template, redirect, url_for, flash, request, jsonify
from app.models import Orders, District, Settlement, BuildingType, Customers, Addresses, TariffPlan
from app.forms import OrderForm
from flask import Blueprint
import sqlalchemy as sa
from flask_login import login_required, current_user
from ..extensions import db

orders = Blueprint('orders', __name__)


@orders.route('/customer/<int:customer_id>/orders/create', methods=['GET', 'POST'])
def create_order(customer_id):
    customer = Customers.query.get_or_404(customer_id)
    form = OrderForm()

    if form.validate_on_submit():
        # Now you can get customer_id from the form data
        customer_id = form.customer_id.data

        address = Addresses(
            settlement_id=form.address.settlement_id.data,
            building_type_id=form.address.building_type_id.data,
            street=form.address.street.data,
            building_number=form.address.building_number.data,
            entrance_number=form.address.entrance_number.data,
            floor_number=form.address.floor_number.data,
            apartment_number=form.address.apartment_number.data,
            coordinates_id=None,  # Set this as needed
            registry_code=form.address.registry_code.data,
        )

        # Add the address to the session and commit
        db.session.add(address)
        db.session.commit()

        # Create an order with the newly created address
        order = Orders(
            customer_id=customer_id,
            address_id=address.id,  # Link to the newly created address
            mobile=form.mobile.data,
            alt_mobile=form.alt_mobile.data,
            tariff_plan_id=form.tariff_plan_id.data,
            comment=form.comment.data,  # Add comment if needed
        )

        db.session.add(order)
        db.session.commit()
        flash('განაცხადი წარმატებით დამატებულია!', 'success')
        return redirect(url_for('customers.view', id=customer_id))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in the {getattr(form, field).label.text} field - {error}", 'danger')
    return render_template('orders/create_order.html', customer=customer, form=form)


@orders.route('/settlements/<int:district_id>')
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

    query = Orders.query.join(Customers).filter(
        sa.or_(
            Orders.mobile.ilike(f'%{search_query}%'),
            Customers.name.ilike(f'%{search_query}%')
        )
    )

    if mobile:
        query = query.filter(Orders.mobile.ilike(f'%{mobile}%'))
    if tariff_plan_id:
        query = query.filter(Orders.tariff_plan_id == tariff_plan_id)
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
    order = Orders.query.get_or_404(order_id)
    return render_template('orders/order_view.html', order=order, active_menu='orders')

@orders.route('/orders/<int:order_id>/edit', methods=['GET', 'POST'])
def edit_order(order_id):
    # Логика для редактирования заказа
    pass