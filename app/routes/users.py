# crm_flask/app/routes/users.py
# Import necessary modules and packages
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, send_file
from flask_login import login_user, login_required, current_user, logout_user
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from ..extensions import db, bcrypt
from ..forms.users import UserCreateForm, LoginForm, UserEditForm
from ..models.users import Users, log_action, UserLog
from ..models.roles import Roles
from ..models.users_roles import UsersRoles
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlparse, urljoin
import pandas as pd
from io import BytesIO

# Define a blueprint for user-related routes
users = Blueprint('users', __name__)

# Set timezone to Tbilisi and get current time
tbilisi_timezone = ZoneInfo('Asia/Tbilisi')
now = datetime.now(tbilisi_timezone)


def is_safe_url(target):
    """
    Checks whether the given URL is safe to redirect to.
    It compares the target URL's scheme and netloc with the request's host.
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@users.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle the user login process.
    If the user is already authenticated, redirect to the dashboard.
    Otherwise, validate the login form, authenticate the user, and log the action.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()
    if form.validate_on_submit():
        # Query the user by email
        user = db.session.scalar(sa.select(Users).where(Users.email == form.email.data))

        # Check if user exists and if password is correct
        if user is None or not bcrypt.check_password_hash(user.passwordHash, form.password.data):
            flash('მონაცემები არ არის სწორი')
            return redirect(url_for('users.login'))

        # Log in the user, remember if checked, and record login action
        login_user(user, remember=form.remember.data)
        log_action(user, 'Login')

        # Update last login time with current time in Tbilisi timezone
        user.lastLogin = datetime.now(tbilisi_timezone)
        db.session.commit()

        # Redirect to the next page if available, else to the dashboard
        return redirect(request.args.get('next') or url_for('dashboard.index'))

    # Render the login page with the form
    return render_template('main/login.html', form=form)


@users.route('/users/user_list', methods=['GET', 'POST'])
@login_required
def users_list():
    """
    Display a paginated list of users.
    Only users with the 'users_list_view' permission can access this page.
    Supports search by name or email.
    """
    if 'users_list_view' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['users_list_view']", 'danger')
        return redirect(url_for('dashboard.index'))

    # Get search query, page number, and per-page count from request arguments
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Validate per_page value
    per_page = per_page if per_page in [10, 50, 100] else 10

    # Build the query filtering by name or email (case-insensitive)
    query = sa.select(Users).filter(
        sa.or_(
            Users.name.ilike(f'%{search_query}%'),
            Users.email.ilike(f'%{search_query}%')
        )
    )

    # Count total number of users matching the query for pagination
    total_count_query = sa.select(sa.func.count()).select_from(
        sa.select(Users).filter(
            sa.or_(
                Users.name.ilike(f'%{search_query}%'),
                Users.email.ilike(f'%{search_query}%')
            )
        )
    )
    total_count = db.session.execute(total_count_query).scalar()

    # Calculate offset based on current page and per_page
    offset = (page - 1) * per_page
    paginated_query = query.limit(per_page).offset(offset)

    # Execute the paginated query and fetch users
    users_query = db.session.execute(paginated_query)
    users = users_query.scalars().all()

    # Define a simple Pagination class to hold pagination data
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

    # Render the user list template with users and pagination info
    return render_template(
        'users/list.html',
        users=users,
        active_menu='administration',
        pagination=pagination,
        per_page=per_page
    )


@users.route('/users/view/<int:user_id>', methods=['GET'])
@login_required
def view_user(user_id):
    """
    Display detailed information about a specific user.
    Only users with the 'user_view' permission can access this page.
    """
    if 'user_view' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['user_view']", 'danger')
        return redirect(url_for('dashboard.index'))

    # Retrieve user by ID or return 404 if not found
    user = Users.query.get_or_404(user_id)
    return render_template('users/view.html', user=user, active_menu='administration')


@users.route('/users/create', methods=['GET', 'POST'])
@login_required
def user_create():
    """
    Create a new user.
    Only users with the 'user_create' permission can access this page.
    Validates the input form, hashes the password, and handles potential integrity errors.
    """
    if 'user_create' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['user_create']", 'danger')
        return redirect(url_for('dashboard.index'))

    form = UserCreateForm()
    if form.validate_on_submit():
        try:
            # Hash the provided password using bcrypt
            hashed_password = bcrypt.generate_password_hash(form.password.data)

            # Create a new Users instance with form data and current timestamp
            user = Users(
                name=form.name.data,
                email=form.email.data,
                passwordHash=hashed_password,
                createdAt=datetime.now(tbilisi_timezone),
                updatedAt=datetime.now(tbilisi_timezone)
            )

            db.session.add(user)
            db.session.commit()

            flash('ახალი მომხმარებელი წარმატებით შექმნილია!', 'success')
            return redirect(url_for('users.users_list'))

        except IntegrityError as e:
            # Log the error for debugging purposes
            db.logging.error(f"Database IntegrityError: {e}")

            # Rollback session in case of error
            db.session.rollback()

            # Check the error message for duplicate entry issues and flash appropriate error messages
            if "Duplicate entry" in str(e.orig):
                if "for key 'users.name'" in str(e.orig):
                    flash('მომხმარებელი ასეთი სახელით უკვე არსებობს. გთხოვთ გამოიყენოთ სხვა სახელი.', 'danger')
                elif "for key 'users.email'" in str(e.orig):
                    flash('მომხმარებელი ასეთი მეილით უკვე არსებობს. გთხოვთ გამოიყენოთ სხვა მეილი.', 'danger')
                else:
                    flash('დაფიქსირდა უნიკალურობის შეცდომა. გთხოვთ გადაამოწმოთ მონაცემები.', 'danger')
            else:
                flash('დაფიქსირდა შეცდომა. გთხოვთ სცადოთ ხელახლა.', 'danger')

    return render_template('users/create.html', form=form, active_menu='administration')


@users.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """
    Edit an existing user's details.
    Only users with the 'user_edit' permission can access this page.
    Updates the user's name, email, status, and optionally updates the password.
    """
    if 'user_edit' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['user_edit']", 'danger')
        return redirect(url_for('dashboard.index'))

    # Retrieve user by id
    user = Users.query.get_or_404(user_id)
    form = UserEditForm(original_email=user.email)

    if form.validate_on_submit():
        # Update user's name and email with new values
        user.name = form.name.data
        user.email = form.email.data
        user.status = int(form.status.data)
        # If a new password is provided, hash it and update the password field
        if form.password.data:
            user.passwordHash = bcrypt.generate_password_hash(form.password.data)

        # Update the updatedAt timestamp
        user.updatedAt = datetime.now(tbilisi_timezone)
        db.session.commit()

        flash('მომხმარებლის ინფორმაცია წარმატებით განახლდა!', 'success')
        return redirect(url_for('users.users_list'))

    elif request.method == 'GET':
        # Pre-fill the form fields with existing user data when the page is first loaded
        form.name.data = user.name
        form.email.data = user.email

    return render_template('users/edit.html',
                           form=form,
                           user=user,
                           active_menu='administration')


@users.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """
    Log out the current user.
    Logs the logout action, removes the user session, and redirects to the login page.
    """
    user = current_user
    log_action(user, 'Logout')
    user_id = current_user.get_id()
    session.pop(user_id, None)  # Remove user session data if exists
    logout_user()
    return redirect(url_for('users.login'))


@users.route('/users/export', methods=['GET'])
@login_required
def users_export():
    """
    Export the list of users to an Excel file.
    Only users with the 'users_export' permission can access this page.
    Retrieves user data, converts it to a pandas DataFrame, adjusts column widths, and sends the file.
    """
    if 'users_export' not in [permission['name'] for permission in current_user.get_permissions(current_user.id)]:
        flash(f"თქვენ არ გაქვთ წვდომა ამ გვერდზე. წვდომის სახელი: ['users_export']", 'danger')
        return redirect(url_for('dashboard.index'))

    # Query all users from the database
    users_query = db.session.execute(sa.select(Users))
    users = users_query.scalars().all()

    # Convert user data to a list of dictionaries with formatted fields
    user_data = [{
        "id": user.id,
        "სახელი": user.name,
        "meili": user.email,
        "სტატუსი": 'აქტიური' if user.status == 1 else 'პასიური',
        "ბოლო ვიზიტი": user.lastLogin.strftime('%Y-%m-%d %H:%M:%S') if user.lastLogin else 'არ არსებობს',
        "ბოლო აქტივობა": user.last_activity.strftime('%Y-%m-%d %H:%M:%S') if user.last_activity else 'არ არსებობს',
        "წარუმატებელი შესვლის მცდელობები": user.failedLoginAttempts,
        "ბლოკირებების რაოდენობა": user.lockOutUntil.strftime(
            '%Y-%m-%d %H:%M:%S') if user.lockOutUntil else 'არ არსებობს',
        "შექმნის თარიღი": user.createdAt.strftime('%Y-%m-%d %H:%M:%S'),
        "განახლების თარიღი": user.updatedAt.strftime('%Y-%m-%d %H:%M:%S')
    } for user in users]

    # Create a pandas DataFrame from the user data
    df = pd.DataFrame(user_data)

    # Create an Excel file in memory using BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Users')

        # Access the active worksheet
        worksheet = writer.sheets['Users']

        # Adjust the width of each column based on the maximum content length
        for col in worksheet.columns:
            max_length = 0
            column = col[0].column_letter  # Get the letter of the column (e.g., 'A')
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            adjusted_width = max_length + 2  # Add some extra space
            worksheet.column_dimensions[column].width = adjusted_width

    # Reset the file pointer to the beginning of the stream
    output.seek(0)

    # Send the file as an attachment for download
    return send_file(output, as_attachment=True, download_name="users.xlsx",
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@users.route('/users/<int:user_id>/logs', methods=['GET'])
@login_required
def user_logs(user_id):
    """
    Display a user's logs.
    Retrieves the user by ID and all associated log records ordered by creation time.
    """
    # Get user by ID or return 404 if not found
    user = Users.query.get_or_404(user_id)

    # Query user logs sorted in descending order (newest first)
    logs = UserLog.query.filter_by(user_id=user_id).order_by(UserLog.created_at.desc()).all()

    return render_template('users/user_logs.html', user=user, logs=logs, active_menu='administration')


@users.route('/users/<int:user_id>/roles', methods=['GET', 'POST'])
@login_required
def user_roles(user_id):
    """
    Manage roles for a given user.
    Displays all available roles, the roles currently assigned to the user,
    and processes form submissions to add or remove roles.
    """
    # Get the user object by ID
    user = Users.query.get(user_id)
    if user is None:
        flash('დაფიქსირდა შეცდომა!', 'danger')
        return redirect(url_for('users.users_list'))

    # Retrieve all roles from the database
    all_roles = Roles.query.all()

    # Get a set of role IDs that are currently associated with this user
    user_roles = {ur.role_id for ur in UsersRoles.query.filter_by(user_id=user_id).all()}

    if request.method == 'POST':
        # Adding a role to the user
        if request.form.get('add_role'):
            role_id = request.form.get('role_id')
            if role_id:
                role = Roles.query.get(role_id)
                if role:
                    # Check if the role is already assigned to the user
                    existing_user_role = UsersRoles.query.filter_by(user_id=user.id, role_id=role.id).first()
                    if not existing_user_role:
                        new_user_role = UsersRoles(user_id=user.id, role_id=role.id)
                        db.session.add(new_user_role)
                        db.session.commit()
                        flash('როლი დამატებულია.', 'success')
                    else:
                        flash('როლი უკვე დამატებული არის.', 'danger')
                else:
                    flash('როლი ვერ მოიძებნა.', 'danger')

        # Removing a role from the user
        elif request.form.get('delete_role'):
            role_id = request.form.get('role_id')
            if role_id:
                user_role = UsersRoles.query.filter_by(user_id=user.id, role_id=role_id).first()
                if user_role:
                    db.session.delete(user_role)
                    db.session.commit()
                    flash('როლი წარმარტაბეთი წაიშალა.', 'success')
                else:
                    flash('როლს არ აქვს კავშირი ტანამშრომლთან.', 'danger')

        # Redirect back to the user roles page after changes
        return redirect(url_for('users.user_roles', user_id=user.id))

    return render_template(
        'users/user_roles.html',
        user=user,
        all_roles=all_roles,
        user_roles=user_roles,
        active_menu='administration'
    )
