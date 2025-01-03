# crm_flask/app/routes/customer_types.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import sqlalchemy as sa
from ..extensions import db
from ..forms.customer_type import CustomerTypeForm
from ..models.customers_type import CustomersType

customer_types = Blueprint('customer_types', __name__)

# Route for listing customer types
@customer_types.route('/customers/customer_types/types_list', methods=['GET'])
@login_required
def types_list():
    # Check if the user has the necessary permission to view customer types
    if 'customers_types_list' not in [perm['name'] for perm in current_user.get_permissions(current_user.id)]:
        flash("წვდომა აკრძალულია. საჭიროა ნებართვა: 'customers_types_list'", 'danger')
        return redirect(url_for('dashboard.index'))

    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    per_page = per_page if per_page in [10, 50, 100] else 10  # Limit per_page options

    # Basic query to filter by customer type name
    query = (
        sa.select(CustomersType)
        .filter(CustomersType.name.ilike(f'%{search_query}%'))
        .order_by(CustomersType.createdAt.desc())
    )

    # Count total records for pagination
    total_count_query = sa.select(sa.func.count()).select_from(CustomersType).filter(
        CustomersType.name.ilike(f'%{search_query}%'))
    total_count = db.session.execute(total_count_query).scalar()

    # Pagination
    offset = (page - 1) * per_page
    paginated_query = query.limit(per_page).offset(offset)
    customer_types_list = db.session.execute(paginated_query).scalars().all()

    # Pagination class
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
        'customers/customer_types.html',
        customer_types=customer_types_list,
        active_menu='customers',
        pagination=pagination,
        per_page=per_page,
        search_query=search_query  # Pass the current search query
    )

# Route to add a new customer type
@customer_types.route('/customers/customer_types/add_type', methods=['GET', 'POST'])
@login_required
def add_type():
    # Check if the user has the necessary permission to add a new customer type
    if 'customers_type_add' not in [perm['name'] for perm in current_user.get_permissions(current_user.id)]:
        flash("წვდომა აკრძალულია. საჭიროა ნებართვა: 'customers_type_add'", 'danger')
        return redirect(url_for('dashboard.index'))
    form = CustomerTypeForm()
    if form.validate_on_submit():
        # Add the new customer type to the database
        new_customer_type = CustomersType(
            name=form.name.data,
            shortName=form.shortName.data,
            category_id=form.category_id.data
        )
        db.session.add(new_customer_type)
        db.session.commit()
        flash('ახალი ტიპი წარმატებით დაემატა!', 'success')  # Flash message in Georgian
        return redirect(url_for('customer_types.types_list'))
    return render_template('customers/add_customer_type.html', form=form, active_menu='customers')

# Route to edit an existing customer type
@customer_types.route('/customers/customer_types/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_customer_type(id):
    customer_type = CustomersType.query.get_or_404(id)
    form = CustomerTypeForm(obj=customer_type)
    if form.validate_on_submit():
        # Update the customer type details
        customer_type.name = form.name.data
        customer_type.shortName = form.shortName.data
        customer_type.category_id = form.category_id.data
        db.session.commit()
        flash('კლიენტის ტიპი წარმატებით დარედაქტირებულია!', 'success')  # Flash message in Georgian
        return redirect(url_for('customer_types.types_list'))
    return render_template('customers/edit_customer_type.html', form=form, customer_type=customer_type, active_menu='customers')
