from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
import sqlalchemy as sa
from ..extensions import db
from ..forms.customers import CustomerForm
from ..models.customers import Customers
from ..models.customer_type import CustomersType

customers = Blueprint('customers', __name__)


@customers.route('/customers/create', methods=['GET', 'POST'])
@login_required
def create():
    if 'customer_create' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash("თქვენ არ გაქვთ წვდომა ამ გვერდზე.", 'danger')
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
        flash('Customer successfully added!', 'success')

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
        # Получаем имя типа клиента
        customer_type = CustomersType.query.filter_by(id=customer.type_id).first()
        type_name = customer_type.name if customer_type else "Unknown"  # Или любое другое значение по умолчанию

        return jsonify({
            "exists": True,
            "customer": {
                "id": customer.id,
                "type_id": customer.type_id,
                "type_name": type_name,  # Добавляем имя типа клиента
                "email": customer.email,
                "mobile": customer.mobile,
                "mobile_second": customer.mobile_second,
                "identification_number": customer.identification_number,
                "name": customer.name
            }
        })
    else:
        return jsonify({"exists": False})

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
#         return redirect(url_for('customers.customer_list'))  # Поменяйте на соответствующий маршрут
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
#         return redirect(url_for('customers.customer_list'))  # Поменяйте на соответствующий маршрут
#
#     return render_template('customers/edit.html', form=form, customer=customer, active_menu='customers')
