// Скрипт для добавления плавного появления и исчезновения формы заказа
const addOrderBtn = document.getElementById('add-order-btn');
const orderFormSection = document.getElementById('order-form-section');
const createOrderFlag = document.getElementById('create-order-flag');
let isOrderFormVisible = false;

addOrderBtn.addEventListener('click', function () {
    if (isOrderFormVisible) {
        orderFormSection.classList.remove('fade-in');
        orderFormSection.classList.add('fade-out');
        createOrderFlag.value = 'false';

        orderFormSection.addEventListener('animationend', function hideOrderForm() {
            if (orderFormSection.classList.contains('fade-out')) {
                orderFormSection.style.display = 'none';
                isOrderFormVisible = false;
            }
            orderFormSection.removeEventListener('animationend', hideOrderForm);
        });
    } else {
        orderFormSection.style.display = 'block';
        orderFormSection.classList.remove('fade-out');
        orderFormSection.classList.add('fade-in');
        createOrderFlag.value = 'true';
        isOrderFormVisible = true;
    }
});

// Логика переключения полей на основе типа клиента
document.getElementById('customer-type').addEventListener('change', function () {
    const type = this.value;
    document.getElementById('individual-fields').style.display = type === '1' ? 'block' : 'none';
    document.getElementById('company-fields').style.display = type === '2' ? 'block' : 'none';
});

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('customer-type').dispatchEvent(new Event('change'));
});

// Логика динамического отображения полей на основе типа здания
document.getElementById('building_type').addEventListener('change', function () {
    const buildingType = this.value;
    document.getElementById('dynamic_fields').innerHTML = buildingType === 'some_type' ? '<input>' : '';
});