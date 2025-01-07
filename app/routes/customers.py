# crm_flask/app/routes/customers.py
from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
import sqlalchemy as sa
from ..extensions import db
from ..forms.customers import CustomerForm
from ..forms.orders import OrderForm
from ..models import Customers, CustomersType, Addresses, Orders, Coordinates, Tasks, Settlement
from sqlalchemy.exc import SQLAlchemyError
from io import BytesIO
import pandas as pd

customers = Blueprint('customers', __name__)


@customers.route('/customers/create', methods=['GET', 'POST'])
@login_required
def create():
    # Check permissions
    if 'customer_create' not in [perm['name'] for perm in current_user.get_permissions(current_user.id)]:
        flash("წვდომა აკრძალულია. საჭიროა ნებართვა: 'customer_create'", 'danger')
        return redirect(url_for('dashboard.index'))

    # Initialize forms
    customer_form = CustomerForm()
    order_form = OrderForm()

    if order_form.address.district_id.data:
        settlements = Settlement.query.filter_by(district_id=order_form.address.district_id.data).all()
        settlement_choices = [(settlement.id, settlement.name) for settlement in settlements]
        order_form.address.settlement_id.choices = settlement_choices

    existing_customer = None
    readonly_fields = False
    customer = None  # To store the created customer

    if customer_form.validate_on_submit() and order_form.validate_on_submit():
        try:
            # Check if the customer already exists based on the identification number
            existing_customer = Customers.query.filter_by(
                identification_number=customer_form.identification_number.data).first()

            if existing_customer:
                # If the customer exists, use their ID to create a new order
                readonly_fields = True  # Set readonly flag
            else:
                # If the customer doesn't exist, create a new customer
                customer = Customers(
                    type_id=customer_form.type_id.data,
                    identification_number=customer_form.identification_number.data,
                    director=customer_form.director.data,
                    name=customer_form.name.data,
                    email=customer_form.email.data,
                    mobile=customer_form.mobile.data,
                    mobile_second=customer_form.mobile_second.data,
                    resident=int(customer_form.resident.data) if customer_form.resident.data else 1,
                    legal_address=customer_form.legal_address.data,
                    actual_address=customer_form.actual_address.data,
                    contact_person_name=customer_form.contact_person_name.data,
                    contact_person_mobile=customer_form.contact_person_mobile.data,
                )
                db.session.add(customer)

            # Create the order for the existing or new customer
            order_form.customer_id.data = existing_customer.id if existing_customer else customer.id  # Set customer_id

            # Check if settlement_id exists in database
            settlement = Settlement.query.filter_by(id=order_form.address.settlement_id.data).first()
            if not settlement:
                flash("Selected settlement does not exist.", 'danger')
                return redirect(url_for('customers.create'))

            coordinates = Coordinates(
                latitude=order_form.address.latitude.data,
                longitude=order_form.address.longitude.data,
            )
            db.session.add(coordinates)
            db.session.commit()

            # Add address to the session
            address = Addresses(
                settlement_id=order_form.address.settlement_id.data,
                building_type_id=order_form.address.building_type_id.data,
                entrance_number=order_form.address.entrance_number.data,
                floor_number=order_form.address.floor_number.data,
                apartment_number=order_form.address.apartment_number.data,
                house_number=order_form.address.house_number.data,
                registry_code=order_form.address.registry_code.data,
                coordinates_id=coordinates.id,
                legal_address=customer_form.legal_address.data,
                actual_address=customer_form.actual_address.data
            )
            db.session.add(address)  # Add the address to the session first

            # Commit changes for address and coordinates to ensure the address_id is available
            db.session.commit()  # Commit the session to persist the address and coordinates

            # automate task to Network Design Department
            description = "ჩართვის შესაძლებლობის მოკვლევა და შესაბამის განყოფილებაზე დაგეგმარება."
            task = Tasks(
                task_type_id=1,  # Use integer
                description=description,
                created_by=current_user.id  # Ensure this is an integer
            )
            db.session.add(task)
            db.session.commit()

            # Now that address and coordinates are added, create the order
            order = Orders(
                customer_id=order_form.customer_id.data,
                address_id=address.id,  # Now we can safely assign the address_id
                tariff_plan_id=order_form.tariff_plan_id.data,
                mobile=order_form.mobile.data,
                alt_mobile=order_form.alt_mobile.data,
                comment=order_form.comment.data,
                legal_address=customer_form.legal_address.data,
                actual_address=customer_form.actual_address.data,
                task_id=task.id
            )
            db.session.add(order)  # Ensure the order is added to the session

            # Commit everything as a transaction
            db.session.commit()
            task.order_id = order.id
            db.session.commit()

            # Redirect to the newly created order page
            flash(
                f"განაცხადი (№{order.id}) წარმატებით შექმნილია! კლიენტი: {customer.name if customer else existing_customer.name}",
                category='success')
            return redirect(url_for('orders.order_view', order_id=order.id))  # Redirect to the order details page

        except SQLAlchemyError as e:
            db.session.rollback()  # Rollback everything if any error occurs
            flash(f"დაფიქსირდა შეცდომა: {str(e)}", 'danger')

    else:
        # Handle form validation errors
        if not customer_form.validate_on_submit():
            for field, errors in customer_form.errors.items():
                for error in errors:
                    flash(f"დაფიქსირდა შეცდომა: {field} ({error})", 'danger')
        if not order_form.validate_on_submit():
            for field, errors in order_form.errors.items():
                for error in errors:
                    flash(f"დაფიქსირდა შეცდომა: {field} ({error})", 'danger')

    return render_template(
        'customers/create.html',
        customer_form=customer_form,
        order_form=order_form,
        readonly_fields=readonly_fields,
        active_menu='customers'
    )


@customers.route('/customer/<int:id>/view', methods=['GET'])
@login_required
def view(id):
    # Check permissions
    if 'customer_view' not in [perm['name'] for perm in current_user.get_permissions(current_user.id)]:
        flash("წვდომა აკრძალულია. საჭიროა ნებართვა: 'customer_view'", 'danger')
        return redirect(url_for('dashboard.index'))
    customer = Customers.query.get_or_404(id)
    orders = Orders.query.filter_by(customer_id=customer.id).all()
    customer.orders = orders
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

    # Limitation of permissible values ​​for per_page
    per_page = per_page if per_page in [10, 50, 100] else 10

    # Start building a query
    query = Customers.query.filter(
        sa.or_(
            Customers.name.ilike(f'%{search_query}%'),
            Customers.identification_number.ilike(f'%{search_query}%')
        )
    )

    # Applying filters
    if type_id:
        query = query.filter(Customers.type_id == type_id)
    if start_date:
        query = query.filter(Customers.created_at >= start_date)
    if end_date:
        query = query.filter(Customers.created_at <= end_date)

    # Applying sorting
    if sort_by == 'created_asc':
        query = query.order_by(Customers.created_at.asc())
    else:
        query = query.order_by(Customers.created_at.desc())

    # Getting the total number of clients
    total_count = query.count()

    # Pagination
    offset = (page - 1) * per_page
    customers = query.limit(per_page).offset(offset).all()

    # Creating a pagination object
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

    # Getting client types for filter dropdown
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

    # Get filter parameters
    search_query = request.args.get('search', '')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    type_id = request.args.get('type_id')

    # start forming a request
    query = sa.select(Customers)

    # Apply filters to the search query
    if search_query:
        query = query.filter(
            sa.or_(
                Customers.name.ilike(f'%{search_query}%'),
                Customers.identification_number.ilike(f'%{search_query}%')
            )
        )

    # Apply filters by client type
    if type_id and type_id != '':
        query = query.filter(Customers.type_id == type_id)

    # Apply filters by dates
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(Customers.created_at >= start_date)

    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        query = query.filter(Customers.created_at <= end_date)

    # Execute the request
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
        form.populate_obj(customer)
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
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'director': customer.director,
                'mobile': customer.mobile,
                'mobile_second': customer.mobile_second
            }), 200
    return jsonify({'exists': False}), 200
