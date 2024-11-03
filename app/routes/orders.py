from flask import render_template, redirect, url_for, flash, request, jsonify
from app.models import Orders, District, Settlement, BuildingType, Customers, Addresses
from app.forms import OrderForm
from flask import Blueprint
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
        flash('Order created successfully!', 'success')
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
