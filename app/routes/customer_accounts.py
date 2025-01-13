# crm_flask/app/routes/customer_accounts.py

from flask import Blueprint, render_template, abort
from flask_login import login_required
from ..models.customer_accounts import CustomerAccount
from ..extensions import db

customer_accounts = Blueprint('customer_accounts', __name__)


@customer_accounts.route('/customer_accounts/<int:account_id>/view', methods=['GET'])
@login_required
def view_customer_account(account_id):
    """
    Представление для отображения деталей CustomerAccount.
    """
    account = CustomerAccount.query.get_or_404(account_id)
    return render_template(
        'customer_accounts/view_customer_account.html',
        account=account,
        active_menu='customer_accounts'
    )
