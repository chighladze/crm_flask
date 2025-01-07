// crm_flask/static/dist/custom/customers/create.js

document.addEventListener("DOMContentLoaded", function () {
    // Получение элементов формы
    const customerTypeSelect = document.getElementById('customer-type');
    const idNumberContainer = document.getElementById('id-number-container');
    const nameContainer = document.getElementById('name-container');
    const directorContainer = document.getElementById('director-container');
    const typeCol = document.getElementById('type-col');
    const buildingTypeSelect = document.getElementById('building_type_id');
    const dynamicFieldsContainer = document.getElementById('dynamic-fields-container');
    const contactPersonContainer = document.getElementById('contact-person-container'); // Контейнер контактного лица

    // Функция для обновления полей клиента на основе типа
    function updateCustomerFields() {
        const type = parseInt(customerTypeSelect.value);
        idNumberContainer.innerHTML = '';
        nameContainer.innerHTML = '';

        if (type === 1) {
            // Физическое лицо
            typeCol.className = 'col-md-4 form-group';
            idNumberContainer.className = 'col-md-4 form-group';
            nameContainer.className = 'col-md-4 form-group';

            const individualFieldsHtml = `
                <label for="identification_number">პირადი ნომერი <span class="text-danger">*</span></label>
                <div class="input-group">
                    <div class="input-group-prepend">
                        <span class="input-group-text"><i class="fas fa-address-card"></i></span>
                    </div>
                    <input class="form-control" placeholder="მაგ: 01012345678" id="identification_number" name="identification_number" required type="text" maxlength="50">
                </div>
            `;
            idNumberContainer.insertAdjacentHTML('beforeend', individualFieldsHtml);

            const individualNameHtml = `
                <label for="name">სახელი და გვარი <span class="text-danger">*</span></label>
                <div class="input-group">
                    <div class="input-group-prepend">
                        <span class="input-group-text"><i class="fas fa-user"></i></span>
                    </div>
                    <input class="form-control" placeholder="მაგ: გიორგი ამბროლაძე" id="name" name="name" required type="text" maxlength="255">
                </div>
            `;
            nameContainer.insertAdjacentHTML('beforeend', individualNameHtml);

            directorContainer.style.display = 'none';

            // Скрыть контейнер контактного лица для физических лиц
            contactPersonContainer.style.display = 'none';
            // Очистить значения полей контактного лица
            document.getElementById('contact_person_name').value = '';
            document.getElementById('contact_person_mobile').value = '';
            // Убрать атрибуты required
            document.getElementById('contact_person_name').removeAttribute('required');
            document.getElementById('contact_person_mobile').removeAttribute('required');
        } else {
            // Юридическое лицо
            typeCol.className = 'col-md-3 form-group';
            idNumberContainer.className = 'col-md-3 form-group';
            nameContainer.className = 'col-md-3 form-group';
            directorContainer.className = 'col-md-3 form-group';

            const companyIdHtml = `
                <label for="identification_number">საიდენტიფიკაციო კოდი <span class="text-danger">*</span></label>
                <div class="input-group">
                    <div class="input-group-prepend">
                        <span class="input-group-text"><i class="fas fa-address-card"></i></span>
                    </div>
                    <input class="form-control" placeholder="მაგ: 405123456" id="identification_number" name="identification_number" required type="text" maxlength="50">
                </div>
            `;
            idNumberContainer.insertAdjacentHTML('beforeend', companyIdHtml);

            const companyNameHtml = `
                <label for="name">კომპანიის სახელი <span class="text-danger">*</span></label>
                <div class="input-group">
                    <div class="input-group-prepend">
                        <span class="input-group-text"><i class="fas fa-home"></i></span>
                    </div>
                    <input class="form-control" placeholder="მაგ: კომპანია 'დელტა'" id="name" name="name" required type="text" maxlength="255">
                </div>
            `;
            nameContainer.insertAdjacentHTML('beforeend', companyNameHtml);

            directorContainer.style.display = 'block';

            // Показать контейнер контактного лица для юридических лиц
            contactPersonContainer.style.display = 'flex';
            // Добавить атрибуты required
            document.getElementById('contact_person_name').setAttribute('required', 'true');
            document.getElementById('contact_person_mobile').setAttribute('required', 'true');
        }
    }

    // Функция для обновления полей здания на основе типа
    function updateBuildingFields() {
        const buildingType = buildingTypeSelect.value;
        dynamicFieldsContainer.innerHTML = '';

        if (buildingType === '2') { // Если "Apartment Building" (пример значения)
            const apartmentFieldsHtml = `
                <div class="col-md-3 form-group">
                    <label for="entrance_number">სადარბაზო</label>
                    <input type="number" placeholder="მაგ: 1" name="entrance_number" class="form-control">
                </div>
                <div class="col-md-3 form-group">
                    <label for="floor_number">სართული</label>
                    <input type="number" placeholder="მაგ: 5" name="floor_number" class="form-control">
                </div>
                <div class="col-md-3 form-group">
                    <label for="apartment_number">ბინის ნომერი <span class="text-danger">*</span></label>
                    <input type="text" placeholder="მაგ: 23" name="apartment_number" class="form-control" required>
                </div>
            `;
            dynamicFieldsContainer.insertAdjacentHTML('beforeend', apartmentFieldsHtml);
        }
    }

    // Обработчик изменения типа клиента
    customerTypeSelect.addEventListener('change', updateCustomerFields);
    // Инициализация полей при загрузке страницы
    updateCustomerFields();

    // Обработчик изменения типа здания
    buildingTypeSelect.addEventListener('change', updateBuildingFields);
    // Инициализация полей при загрузке страницы
    updateBuildingFields();

    // Валидация формы перед отправкой
    document.getElementById('customer-form').addEventListener('submit', function (e) {
        if (!document.getElementById('settlement-select').value) {
            e.preventDefault();
            alert('გთხოვთ აირჩიოთ დასახლება');
        }
    });

    // Логика для динамической загрузки населенных пунктов
    document.getElementById('district-select').addEventListener('change', function () {
        const districtId = this.value;
        const settlementSelect = document.getElementById('settlement-select');
        const csrfToken = document.querySelector('[name=csrf_token]').value;

        settlementSelect.innerHTML = '<option value="">აირჩიეთ დასახლება</option>';

        if (districtId) {
            fetch(`/settlements/${districtId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.settlements) {
                        data.settlements.forEach(function (settlement) {
                            const option = document.createElement('option');
                            option.value = settlement.id;
                            option.textContent = settlement.name;
                            settlementSelect.appendChild(option);
                        });
                        // Инициализация select2 после добавления опций
                        $(settlementSelect).select2({
                            placeholder: "აირჩიეთ დასახლება",
                            allowClear: true
                        });
                    } else if (data.error) {
                        alert(data.error);
                    }
                })
                .catch(error => console.error('Error fetching settlements:', error));
        }
    });

    // Инициализация загрузки населенных пунктов при загрузке страницы
    document.getElementById('district-select').dispatchEvent(new Event('change'));

    // Обработчик ввода идентификационного номера для проверки существования клиента
    document.getElementById('customer-form').addEventListener('input', function (event) {
        if (event.target.id === 'identification_number') {
            const identificationNumber = event.target.value;
            const csrfToken = document.querySelector('[name=csrf_token]').value;
            const registerButton = document.getElementById('register-button'); // Кнопка регистрации

            // Если введен идентификационный номер
            if (identificationNumber.length > 0) {
                fetch('/customers/check_identification', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ identification_number: identificationNumber })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.exists) {
                            // Заполнение формы данными существующего клиента
                            document.getElementById('name').value = data.name || 'მონაცემები ვერ მოიძბენა';
                            document.getElementById('email').value = data.email || 'მონაცემები ვერ მოიძბენა';
                            document.getElementById('director').value = data.director || 'მონაცემები ვერ მოიძბენა';
                            document.getElementById('mobile').value = data.mobile || 'მონაცემები ვერ მოიძბენა';
                            document.getElementById('mobile_second').value = data.mobile_second || 'მონაცემები ვერ მოიძბენა';

                            // Установка полей как readonly
                            document.getElementById('name').setAttribute('readonly', 'true');
                            document.getElementById('email').setAttribute('readonly', 'true');
                            document.getElementById('director').setAttribute('readonly', 'true');
                            document.getElementById('mobile').setAttribute('readonly', 'true');
                            document.getElementById('mobile_second').setAttribute('readonly', 'true');

                            // Установка скрытого поля с ID клиента
                            const customerIdInput = document.getElementById('customer-id');
                            if (customerIdInput) {
                                customerIdInput.value = data.id;
                            }

                            // Скрыть кнопку регистрации, если клиент уже существует
                            // registerButton.style.display = 'none';
                        } else {
                            // Очистка полей и снятие readonly, если клиент не найден
                            document.getElementById('name').value = '';
                            document.getElementById('email').value = '';
                            document.getElementById('director').value = '';
                            document.getElementById('mobile').value = '';
                            document.getElementById('mobile_second').value = '';

                            document.getElementById('name').removeAttribute('readonly');
                            document.getElementById('email').removeAttribute('readonly');
                            document.getElementById('director').removeAttribute('readonly');
                            document.getElementById('mobile').removeAttribute('readonly');
                            document.getElementById('mobile_second').removeAttribute('readonly');

                            // Показать кнопку регистрации, если клиент не найден
                            registerButton.style.display = 'inline-block';
                        }
                    })
                    .catch(error => console.error('Error checking identification:', error));
            } else {
                // Если поле пустое, показать кнопку регистрации и сделать поля редактируемыми
                registerButton.style.display = 'inline-block';

                document.getElementById('name').removeAttribute('readonly');
                document.getElementById('email').removeAttribute('readonly');
                document.getElementById('director').removeAttribute('readonly');
                document.getElementById('mobile').removeAttribute('readonly');
                document.getElementById('mobile_second').removeAttribute('readonly');

                // Очистить скрытое поле с ID клиента
                const customerIdInput = document.getElementById('customer-id');
                if (customerIdInput) {
                    customerIdInput.value = '';
                }
            }
        }
    });
});
