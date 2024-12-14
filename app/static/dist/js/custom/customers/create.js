// crm_flask/static/dist/custom/customers/create.js

document.addEventListener("DOMContentLoaded", function () {
    // Event listener for changes in the identification number field
    document.getElementById('customer-form').addEventListener('input', function (event) {
        if (event.target.id === 'identification_number') {
            const identificationNumber = event.target.value;
            const csrfToken = document.getElementById('csrf_token').value;
            const registerButton = document.getElementById('register-button'); // Registration button element

            // If the identification number is entered
            if (identificationNumber.length > 0) {
                fetch('/customers/check_identification', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({identification_number: identificationNumber})
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.exists) {
                            // Fill the form with the existing customer's data
                            document.getElementById('name').value = data.name || 'Data not found';
                            document.getElementById('email').value = data.email || 'Data not found';
                            document.getElementById('mobile').value = data.mobile || 'Data not found';
                            document.getElementById('mobile_second').value = data.mobile_second || 'Data not found';

                            // Set the fields as readonly
                            document.getElementById('name').setAttribute('readonly', 'true');
                            document.getElementById('email').setAttribute('readonly', 'true');
                            document.getElementById('mobile').setAttribute('readonly', 'true');
                            document.getElementById('mobile_second').setAttribute('readonly', 'true');

                            // If necessary, update hidden fields, for example, with the customer's id
                            document.getElementById('customer-id').value = data.id;

                            // Hide the registration button if the customer already exists
                            registerButton.style.display = 'none';

                            // Show the modal with existing customer details
                            $('#customerExistsModal').modal('show');
                        } else {
                            // Clear the fields and remove readonly if the customer is not found
                            document.getElementById('name').value = '';
                            document.getElementById('email').value = '';
                            document.getElementById('mobile').value = '';
                            document.getElementById('mobile_second').value = '';

                            document.getElementById('name').removeAttribute('readonly');
                            document.getElementById('email').removeAttribute('readonly');
                            document.getElementById('mobile').removeAttribute('readonly');
                            document.getElementById('mobile_second').removeAttribute('readonly');

                            // Show the registration button if no customer is found
                            registerButton.style.display = 'inline-block';
                        }
                    })
                    .catch(error => console.error('Error:', error));
            } else {
                // If the field is empty, show the registration button and make the fields editable
                registerButton.style.display = 'inline-block';

                document.getElementById('name').removeAttribute('readonly');
                document.getElementById('email').removeAttribute('readonly');
                document.getElementById('mobile').removeAttribute('readonly');
                document.getElementById('mobile_second').removeAttribute('readonly');
            }
        }
    });



// Logic to toggle fields based on customer type
document.getElementById('customer-type').addEventListener('change', function () {
    const type = this.value;
    document.getElementById('individual-fields').style.display = type === '1' ? 'block' : 'none';
    document.getElementById('company-fields').style.display = type > '1' ? 'block' : 'none';

    // Change labels for identification number and name
    const personalLabel = document.querySelector('label[for="identification_number"]');
    const nameLabel = document.querySelector('label[for="name"]');

    if (type === '1') {
        personalLabel.textContent = 'პირადი ნომერი'; // Update to "Personal Number" for individuals
        nameLabel.textContent = 'სახელი და გვარი'; // Update to "Full Name"
    } else {
        personalLabel.textContent = 'საიდენტიფიკაციო კოდი'; // Update to "Identification Code" for companies
        nameLabel.textContent = 'კომპანიის სახელი'; // Update to "Company Name"
    }
});

// Initialize fields based on customer type when the page loads
document.getElementById('customer-type').dispatchEvent(new Event('change'));

// Logic for dynamically displaying fields based on building type selection
document.getElementById('building_type_id').addEventListener('change', function () {
    const buildingTypeId = this.value;
    const dynamicFields = document.getElementById('dynamic_fields');
    dynamicFields.innerHTML = ''; // Clear current dynamic fields

    if (buildingTypeId === '2') { // If "Apartment Building" (example value)
        dynamicFields.innerHTML = `
                <div class="form-group">
                    <label for="entrance_number">სადარბაზო</label>
                    <input type="number" name="entrance_number" class="form-control">
                </div>
                <div class="form-group">
                    <label for="floor_number">სართული</label>
                    <input type="number" name="floor_number" class="form-control">
                </div>
                <div class="form-group">
                    <label for="apartment_number">ბინის ნომერი</label>
                    <input type="text" name="apartment_number" class="form-control" required>
                </div>`;
    }
});

// Logic to dynamically load settlements based on selected district
document.getElementById('district-select').addEventListener('change', function () {
    const districtId = this.value;
    const settlementSelect = document.getElementById('settlement-select');
    const csrfToken = document.querySelector('[name=csrf_token]').value;

    // Очистить текущие поселения в селекте
    settlementSelect.innerHTML = '<option value="">აირჩიეთ დასახლება</option>';

    if (districtId) {
        // Получение поселений для выбранного района
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
                    // Заполняем селект поселениями
                    data.settlements.forEach(function (settlement) {
                        const option = document.createElement('option');
                        option.value = settlement.id;
                        option.textContent = settlement.name;
                        settlementSelect.appendChild(option);
                    });
                } else if (data.error) {
                    alert(data.error);
                }
            })
            .catch(error => console.error('Error fetching settlements:', error));
    }
});

// Вызвать change event при начальной загрузке, если это нужно
document.getElementById('district-select').dispatchEvent(new Event('change'));

})
;
