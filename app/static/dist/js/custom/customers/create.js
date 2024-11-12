// project path: crm_flask/app/static/dist/js/custom/create.js


// Event listener to handle input changes on the identification number field
document.getElementById('customer-form').addEventListener('input', function (event) {
    if (event.target.id === 'identification_number') {
        const identificationNumber = event.target.value;
        const csrfToken = document.getElementById('csrf_token').value;
        const registerButton = document.getElementById('register-button'); // Registration button element

        if (identificationNumber.length > 0) {
            fetch('/customers/check_identification', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({identification_number: identificationNumber})
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP შეცდომა: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.exists) {
                        // Fill the modal with existing customer information
                        document.getElementById('customerName').innerText = data.name || 'ინფორმაცია არ არის';
                        document.getElementById('customerEmail').innerText = data.email || 'ინფორმაცია არ არის';
                        document.getElementById('customerPhone').innerText = data.phone || 'ინფორმაცია არ არის';
                        document.getElementById('customerAddress').innerText = data.address || 'ინფორმაცია არ არის';

                        // Update links to view and edit the existing customer's profile
                        document.getElementById('viewCustomerLink').href = `/customer/${data.id}/view`;
                        document.getElementById('editCustomerLink').href = `/customers/edit/${data.id}`;

                        // Hide the registration button if the customer already exists
                        registerButton.style.display = 'none';

                        // Show the modal with the existing customer details
                        $('#customerExistsModal').modal('show');
                    } else {
                        // Show the registration button if no customer is found
                        registerButton.style.display = 'inline-block';
                    }
                })
                .catch(error => console.error('Error:', error));
        } else {
            // Show the registration button if the field is empty
            registerButton.style.display = 'inline-block';
        }
    }
});

// Script to toggle order form visibility with fade-in and fade-out animations
const addOrderBtn = document.getElementById('add-order-btn');
const orderFormSection = document.getElementById('order-form-section');
const createOrderFlag = document.getElementById('create-order-flag');
let isOrderFormVisible = false;

addOrderBtn.addEventListener('click', function () {
    if (isOrderFormVisible) {
        orderFormSection.classList.remove('fade-in');
        orderFormSection.classList.add('fade-out');
        createOrderFlag.value = 'false';

        // Listen for animation end to hide the order form after fade-out
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

// Logic to switch fields based on customer type
document.getElementById('customer-type').addEventListener('change', function () {
    const type = this.value;
    document.getElementById('individual-fields').style.display = type === '1' ? 'block' : 'none';
    document.getElementById('company-fields').style.display = type === '2' ? 'block' : 'none';
});

// Initialize fields based on customer type when the page loads
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('customer-type').dispatchEvent(new Event('change'));
});

// Logic to dynamically display fields based on building type selection
document.getElementById('building_type').addEventListener('change', function () {
    const buildingType = this.value;
    document.getElementById('dynamic_fields').innerHTML = buildingType === 'some_type' ? '<input>' : '';
});
