// crm_flask/app/static/dist/js/custom/orders/order_view.js

document.addEventListener('DOMContentLoaded', function () {
    const taskStatus = document.getElementById('taskStatus');
    const addButton = document.getElementById('addButton');
    const taskCurrentStatusElement = document.getElementById('taskCurrentStatus');
    const divisionSelectContainer = document.getElementById('divisionSelectContainer');
    const divisionSelect = document.getElementById('divisionSelect');

    let initialStatus;

    // Function to set the initial status
    function setInitialStatus() {
        initialStatus = taskCurrentStatusElement.getAttribute('data-status-id');
        addButton.style.display = 'none';
        divisionSelectContainer.style.display = 'none'; // Hide division select on modal open
    }

    // Handle status change
    taskStatus.addEventListener('change', function () {
        if (taskStatus.value !== initialStatus) {
            addButton.style.display = 'inline-block';
        } else {
            addButton.style.display = 'none';
            divisionSelectContainer.style.display = 'none'; // Hide if status reverted
        }
    });

    // Fetch divisions
    function fetchDivisions() {
        // Optionally, you can pass department_id if needed
        // For example: /api/divisions?department_id=1
        return fetch('/divisions/get_divisions')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => data.divisions)
            .catch(error => {
                console.error('Error fetching divisions:', error);
                throw error;
            });
    }

    // Populate the division select with fetched divisions
    function populateDivisionSelect(divisions) {
        // Clear existing options except the first placeholder
        divisionSelect.innerHTML = '<option value="" disabled selected>განყოფილების არჩევა</option>';
        divisions.forEach(division => {
            const option = document.createElement('option');
            option.value = division.id;
            option.textContent = division.name;
            divisionSelect.appendChild(option);
        });
    }

    // Handle "+" button click
    addButton.addEventListener('click', function () {
        // Fetch divisions from the API
        fetchDivisions()
            .then(divisions => {
                if (divisions.length === 0) {
                    alert('No divisions available.');
                    return;
                }
                populateDivisionSelect(divisions);
                divisionSelectContainer.style.display = 'block'; // Show the select container
            })
            .catch(error => {
                console.error('Error fetching divisions:', error);
                alert('Failed to load divisions. Please try again later.');
            });
    });

    // Initialize the modal
    $('#taskModal').on('show.bs.modal', function () {
        setInitialStatus(); // Set initial status when modal is opened
    });
});

// Function to show task details in the modal
function showTaskDetails(taskId) {
    // Reset modal content
    document.getElementById('taskDetailsContent').style.display = 'none';
    document.getElementById('errorMessage').style.display = 'none';
    document.getElementById('loadingSpinner').style.display = 'block';

    fetch(`/tasks/details/${taskId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load task details');
            }
            return response.json();
        })
        .then(data => {
            // Populate task data
            document.getElementById('taskId').textContent = data.id;
            document.getElementById('taskDivision').textContent = data.division ? data.division.name : 'არ არის მითითებული';
            document.getElementById('taskType').textContent = data.task_type.name || 'არ არის მითითებული';
            document.getElementById('taskCurrentStatus').textContent = data.current_status.name || 'არ არის მითითებული';
            document.getElementById('taskDescription').value = data.description || 'არ არის მითითებული';

            // Populate status dropdown
            const taskStatus = document.getElementById('taskStatus');
            taskStatus.innerHTML = '';
            data.statuses.forEach(status => {
                const option = document.createElement('option');
                option.value = status.id;
                option.textContent = status.name;
                if (status.id === data.current_status.id) {
                    option.selected = true;
                }
                taskStatus.appendChild(option);
            });

            // Show the content and hide the spinner
            document.getElementById('loadingSpinner').style.display = 'none';
            document.getElementById('taskDetailsContent').style.display = 'block';
        })
        .catch(error => {
            console.error(error);
            document.getElementById('loadingSpinner').style.display = 'none';
            document.getElementById('errorMessage').style.display = 'block';
        });
}

// Handle form submission for updating the task
document.getElementById('taskEditForm').addEventListener('submit', function (event) {
    event.preventDefault();
    const taskId = document.getElementById('taskId').textContent;
    const formData = new FormData(this);

    // Optionally, you can validate division selection here
    const divisionSelect = document.getElementById('divisionSelect');
    const selectedDivisionId = divisionSelect.value;

    // If divisionSelectContainer is visible, ensure a division is selected
    if (divisionSelectContainer.style.display === 'block' && !selectedDivisionId) {
        alert('Please select a division.');
        return;
    }

    fetch(`/tasks/update/${taskId}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': formData.get('csrf_token')
        },
        body: formData
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.message || 'Failed to update task');
                });
            }
            return response.json();
        })
        .then(data => {
            // Close the modal
            $('#taskModal').modal('hide');
            // Show success toast
            $('#successToast').toast('show');
            // Update the task row in the table
            updateTaskRow(taskId, data.new_status, data.new_division);
        })
        .catch(error => {
            console.error(error);
            // Show error toast
            $('#errorToast').toast('show');
        });
});

// Function to update the task row in the table
function updateTaskRow(taskId, newStatus, newDivision) {
    const statusCell = document.getElementById(`task-status-${taskId}`);
    if (statusCell) {
        statusCell.textContent = newStatus.name;
        statusCell.className = `badge bg-${newStatus.bootstrap_class} text-capitalize`;
    }

    const divisionCell = document.getElementById(`task-division-${taskId}`);
    if (divisionCell && newDivision) {
        divisionCell.textContent = newDivision.name;
    }
}

// Function to transfer account (implement as needed)
function accountTransfer(taskId) {
    // Implement account transfer logic here
    alert(`Transfer account for task ID: ${taskId}`);
}

// Initialize Toast notifications
$(document).ready(function () {
    $('.toast').toast({ delay: 3000 });
});
