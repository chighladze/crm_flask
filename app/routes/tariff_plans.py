import datetime
import time
from io import BytesIO

import pandas as pd
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from ..models.tariff_plans import TariffPlan
from ..models.customers import CustomersType
from ..models.currencies import Currencies
from ..models.connection_technology import ConnectionTechnology
from ..extensions import db
from ..forms.tariff_plans import TariffPlanForm

# Create a blueprint for tariff plans
tariff_plans = Blueprint('tariff_plans', __name__)


@tariff_plans.route('/tariff_plan/tariff_list', methods=['GET'])
def tariff_list():
    # Получение параметров поиска, фильтрации и пагинации
    search_query = request.args.get('search', '').strip()
    currency_id = request.args.get('currency_id', type=int)  # ID валюты для фильтрации
    page = request.args.get('page', 1, type=int)  # Текущая страница, по умолчанию 1
    per_page = request.args.get('per_page', 10, type=int)  # Количество элементов на странице, по умолчанию 10

    # Создание базового запроса для тарифов
    query = TariffPlan.query

    # Применение поиска по названию тарифа
    if search_query:
        query = query.filter(TariffPlan.name.ilike(f'%{search_query}%'))

    # Применение фильтрации по валюте
    if currency_id:
        query = query.filter(TariffPlan.currency_id == currency_id)

    # Пагинация результатов
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    tariffs = pagination.items  # Элементы на текущей странице

    # Получение списка валют для фильтрации
    currencies = Currencies.query.all()

    return render_template(
        'tariff_plans/tariff_list.html',
        tariffs=tariffs,
        pagination=pagination,
        search_query=search_query,
        currency_id=currency_id,
        currencies=currencies,
        per_page=per_page
    )



@tariff_plans.route('/tariff_plan/add_tariff', methods=['GET'])
def add_tariff():
    form = TariffPlanForm()
    # Populate select fields with choices from the database, including currency symbol
    form.customer_type_id.choices = [(ct.id, ct.name) for ct in CustomersType.query.all()]
    form.currency_id.choices = [
        (c.id, f"({c.symbol} - {c.code}) {c.name}") for c in Currencies.query.all()
    ]
    form.technology_id.choices = [(t.id, t.name) for t in ConnectionTechnology.query.all()]

    # Handle tariff creation if form is valid
    if form.validate_on_submit():
        new_tariff = TariffPlan(
            name=form.name.data,
            customer_type_id=form.customer_type_id.data,
            price=form.price.data,
            currency_id=form.currency_id.data,
            technology_id=form.technology_id.data,
            internet_download_speed=form.internet_download_speed.data,
            internet_upload_speed=form.internet_upload_speed.data,
            internet_min_download_speed=form.internet_min_download_speed.data,
            internet_min_upload_speed=form.internet_min_upload_speed.data,
            internet_data_limit=form.internet_data_limit.data,
            internet_unlimited=form.internet_unlimited.data
        )
        db.session.add(new_tariff)
        db.session.commit()
        flash('ტარიფი წარმატებით შეიქმნა!', 'success')
        return redirect(url_for('tariff_plans.tariff_list'))

    return render_template('tariff_plans/add_tariff.html', form=form)


# Route for editing an existing tariff
@tariff_plans.route('/tariff_plan/edit/<int:id>', methods=['GET', 'POST'])
def edit_tariff(id):
    tariff = TariffPlan.query.get_or_404(id)
    form = TariffPlanForm(obj=tariff)

    # Populate select fields with choices from the database, including currency symbol
    form.customer_type_id.choices = [(ct.id, ct.name) for ct in CustomersType.query.all()]
    form.currency_id.choices = [
        (c.id, f"({c.symbol} - {c.code}) {c.name}") for c in Currencies.query.all()
    ]
    form.technology_id.choices = [(t.id, t.name) for t in ConnectionTechnology.query.all()]

    # Update the tariff if form is valid
    if form.validate_on_submit():
        tariff.name = form.name.data
        tariff.customer_type_id = form.customer_type_id.data
        tariff.price = form.price.data
        tariff.currency_id = form.currency_id.data
        tariff.technology_id = form.technology_id.data
        tariff.internet_download_speed = form.internet_download_speed.data
        tariff.internet_upload_speed = form.internet_upload_speed.data
        tariff.internet_min_download_speed = form.internet_min_download_speed.data
        tariff.internet_min_upload_speed = form.internet_min_upload_speed.data
        tariff.internet_data_limit = form.internet_data_limit.data
        tariff.internet_unlimited = form.internet_unlimited.data
        tariff.description = form.description.data

        db.session.commit()
        flash('ტარიფი წარმატებით განახლდა!', 'success')
        return redirect(url_for('tariff_plans.tariff_list'))

    return render_template('tariff_plans/edit_tariff.html', form=form, tariff=tariff)


@tariff_plans.route('/tariffs/export', methods=['GET'])
def export_tariffs():
    # Retrieve all tariffs from the database
    tariffs = TariffPlan.query.all()

    # Create a dictionary with tariff data
    data = {
        "ID": [tariff.id for tariff in tariffs],
        "სახელი": [tariff.name for tariff in tariffs],
        "კლიენტის ტიპი": [tariff.customer_type.name for tariff in tariffs],
        "ფასი": [tariff.price for tariff in tariffs],
        "ვალუტა": [tariff.currency.name for tariff in tariffs],
        "დაკავშირების ტექნოლოგია": [tariff.connection_technology.name for tariff in tariffs],
        "ჩამოტვირთვის სიჩქარე": [tariff.internet_download_speed for tariff in tariffs],
        "ატვირთვის სიჩქარე": [tariff.internet_upload_speed for tariff in tariffs],
        "მინ. ჩამოტვირთვის სიჩქარე": [tariff.internet_min_download_speed for tariff in tariffs],
        "მინ. ატვირთვის სიჩქარე": [tariff.internet_min_upload_speed for tariff in tariffs],
        "მონაცემთა ლიმიტი": [tariff.internet_data_limit for tariff in tariffs],
        "უსაზღვრო ინტერნეტი": ["კი" if tariff.internet_unlimited else "არა" for tariff in tariffs],
    }

    # Create a DataFrame and write it to an Excel file in memory
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Tariffs')

    output.seek(0)
    return send_file(output, as_attachment=True, download_name=f"tariff_plasn_{datetime.datetime.now()}.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
