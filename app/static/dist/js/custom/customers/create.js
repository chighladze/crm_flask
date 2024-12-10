// crm_flask/static/dist/custom/customers/create.js

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
                body: JSON.stringify({ identification_number: identificationNumber })
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error: ${response.status}`);
                    }
                    return response.json();
                })
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

// When the page loads, set the readonly fields based on the flag passed from the server
document.addEventListener("DOMContentLoaded", function() {
    const readonlyFields = document.getElementById('readonly_fields').value === 'True'; // Get the readonly flag value from hidden input

    if (readonlyFields) {
        const readonlyElements = ['name', 'email', 'mobile', 'mobile_second']; // List of fields to make readonly

        readonlyElements.forEach(function(id) {
            const element = document.getElementById(id);
            if (element) {
                element.setAttribute('readonly', 'true');
            }
        });
    }
});

// Logic to toggle fields based on customer type
document.getElementById('customer-type').addEventListener('change', function () {
    const type = this.value;
    document.getElementById('individual-fields').style.display = type === '1' ? 'block' : 'none';
    document.getElementById('company-fields').style.display = type >= '2' ? 'block' : 'none';
});

// Initialize fields based on customer type when the page loads
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('customer-type').dispatchEvent(new Event('change'));
});

// Logic for dynamically displaying fields based on building type selection
document.getElementById('building_type').addEventListener('change', function () {
    const buildingType = this.value;
    document.getElementById('dynamic_fields').innerHTML = buildingType === 'some_type' ? '<input>' : '';
});

