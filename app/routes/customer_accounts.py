# crm_flask/app/routes/customer_accounts.py

from flask import Blueprint, render_template, abort, request, jsonify
from flask_login import login_required
from ..models import CustomerAccount, Customers
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


@customer_accounts.route('/api/customer_accounts_list', methods=['GET'])
@login_required
def api_customer_accounts_list():
    """
    API endpoint для получения списка customer_accounts с фильтрацией и пагинацией.
    """
    # Получаем параметры фильтрации из запроса
    account_pay_number = request.args.get('account_pay_number', '')
    customer_name = request.args.get('customer_name', '')
    mac_address = request.args.get('mac_address', '')
    status = request.args.get('status', '')
    tariff_plan_id = request.args.get('tariff_plan_id', type=int)
    device_type = request.args.get('device_type', '')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Предполагается, что связь между CustomerAccount и Customers
    # настроена (например, account.customer)
    query = CustomerAccount.query.join(CustomerAccount.customer).join(CustomerAccount.tariff_plan)

    # Пример фильтрации по номеру счета
    if account_pay_number:
        query = query.filter(CustomerAccount.account_pay_number.ilike(f'%{account_pay_number}%'))
    # По имени клиента
    if customer_name:
        query = query.filter(Customers.name.ilike(f'%{customer_name}%'))
    # По MAC адресу
    if mac_address:
        query = query.filter(CustomerAccount.mac_address.ilike(f'%{mac_address}%'))
    # По статусу
    if status:
        query = query.filter(CustomerAccount.status == status)
    # По тарифному плану
    if tariff_plan_id:
        query = query.filter(CustomerAccount.tariff_plan_id == tariff_plan_id)
    # По типу устройства
    if device_type:
        query = query.filter(CustomerAccount.device_type == device_type)
    # Фильтрация по дате создания
    if start_date:
        query = query.filter(CustomerAccount.created_at >= start_date)
    if end_date:
        query = query.filter(CustomerAccount.created_at <= end_date)

    # Выполняем пагинацию
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    accounts = pagination.items

    # Формирование ответа
    accounts_data = []
    for account in accounts:
        accounts_data.append({
            "id": account.id,
            "account_pay_number": account.account_pay_number,
            "customer_name": account.customer.name if account.customer else "N/A",
            "mac_address": account.mac_address,
            "ip_address": account.ip_address,
            "tariff_plan": account.tariff_plan.name if account.tariff_plan else "N/A",
            "device_name": account.device_name,
            "device_type": account.device_type,
            "status": account.status,
            "created_at": account.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": account.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        })

    response = {
        "accounts": accounts_data,
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


@customer_accounts.route('/customer_accounts/customer_accounts_list', methods=['GET'])
@login_required
def customer_accounts_list():
    customers = CustomerAccount.query.all()
    return render_template('customer_accounts/customer_accounts_list.html',
                           customers=customers,
                           active_menu='customer_accounts')
