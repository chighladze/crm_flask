document.addEventListener('DOMContentLoaded', function () {
    // Using jQuery for element selection
    const $taskStatus = $('#taskStatus');
    const $addButton = $('#addButton');
    const $taskCurrentStatusElement = $('#taskCurrentStatus');
    const $divisionSelectContainer = $('#divisionSelectContainer');
    const $divisionSelect = $('#divisionSelect');
    const $taskTypeSelect = $('#taskTypeSelect');
    const $taskTypeContainer = $('#taskTypeContainer');
    const $taskTypeInputContainer = $('#taskTypeInputContainer');
    const $taskTypeInput = $('#taskTypeInput');
    const $actionType = $('#actionType'); // Hidden input to track action

    let initialStatus;
    let isCreatingSubtask = false; // Flag to track if "+" was clicked

    // Function to set initial status and hide additional fields
    function setInitialStatus() {
        initialStatus = $taskCurrentStatusElement.data('status-id');
        $addButton.hide();
        isCreatingSubtask = false; // Reset the flag
        $actionType.val('update_status'); // Default action

        // Hide all additional fields
        $divisionSelectContainer.hide();
        $taskTypeContainer.hide();
        $taskTypeInputContainer.hide();
        $taskTypeSelect.html('<option value="" disabled selected>აირჩიეთ ტიპი</option>');
        $taskTypeInput.val('');
    }

    // Handle status change
    $taskStatus.on('change', function () {
        if ($(this).val() !== initialStatus) {
            $addButton.fadeIn(); // Show "+" button
        } else {
            $addButton.fadeOut(); // Hide "+" button
            // Reset action type if status reverted
            isCreatingSubtask = false;
            $actionType.val('update_status');
            // Hide additional fields
            $divisionSelectContainer.slideUp();
            $taskTypeContainer.slideUp();
            $taskTypeInputContainer.slideUp();
            $taskTypeSelect.html('<option value="" disabled selected>აირჩიეთ ტიპი</option>');
            $taskTypeInput.val('');
        }
    });

    // Handle "+" button click
    $addButton.on('click', function () {
        isCreatingSubtask = true; // Set the flag
        $actionType.val('create_subtask'); // Update action type
        // Fetch and populate divisions
        fetchDivisions()
            .then(divisions => {
                if (divisions.length === 0) {
                    alert('No divisions available.');
                    return;
                }
                populateDivisionSelect(divisions);
                $divisionSelectContainer.slideDown(); // Show division select
            })
            .catch(error => {
                console.error('Error fetching divisions:', error);
                alert('Failed to load divisions. Please try again later.');
            });
    });

    // Fetch divisions from the server
    function fetchDivisions() {
        return fetch('/tasks/get_divisions')
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

    // Populate the division select dropdown
    function populateDivisionSelect(divisions) {
        $divisionSelect.html('<option value="" disabled selected>განყოფილების არჩევა</option>');
        divisions.forEach(division => {
            const option = $('<option></option>').attr('value', division.id).text(division.name);
            $divisionSelect.append(option);
        });
    }

    // Handle division selection to fetch task types
    $divisionSelect.on('change', function () {
        const selectedDivisionId = $(this).val();
        if (selectedDivisionId) {
            fetchTaskTypes(selectedDivisionId)
                .then(taskTypes => {
                    populateTaskTypeSelect(taskTypes);
                    $taskTypeContainer.slideDown(); // Show task type select
                })
                .catch(error => {
                    console.error('Error fetching task types:', error);
                    alert('Failed to load task types. Please try again later.');
                });
        } else {
            $taskTypeSelect.html('<option value="" disabled selected>აირჩიეთ ტიპი</option>');
            $taskTypeContainer.slideUp();
            $taskTypeInputContainer.slideUp();
            $taskTypeInput.val('');
        }
    });

    // Fetch task types based on division
    function fetchTaskTypes(divisionId) {
        return fetch(`/tasks/task_types/get_task_types/${divisionId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch task types');
                }
                return response.json();
            })
            .then(data => data.task_types)
            .catch(error => {
                console.error('Error fetching task types:', error);
                throw error;
            });
    }

    // Populate the task type select dropdown
    function populateTaskTypeSelect(taskTypes) {
        $taskTypeSelect.html('<option value="" disabled selected>აირჩიეთ ტიპი</option>');
        taskTypes.forEach(taskType => {
            const option = $('<option></option>').attr('value', taskType.id).text(taskType.name);
            $taskTypeSelect.append(option);
        });
        $taskTypeInputContainer.slideUp();
        $taskTypeInput.val('');
    }

    // Show or hide the task description input based on task type selection
    $taskTypeSelect.on('change', function () {
        if ($(this).val()) {
            $taskTypeInputContainer.slideDown(); // Show description input
        } else {
            $taskTypeInputContainer.slideUp(); // Hide description input
            $taskTypeInput.val('');
        }
    });

    // Initialize the modal when it is shown
    $('#taskModal').on('show.bs.modal', function () {
        setInitialStatus(); // Reset the form
    });

    // Handle form submission
    $('#taskEditForm').on('submit', function (event) {
        event.preventDefault();
        const taskId = $('#taskId').text();
        const formData = new FormData(this);

        if (isCreatingSubtask) {
            // Creating a subtask
            const subtaskData = {
                parent_task_id: taskId,
                description: formData.get('task_type_description'),
                status_id: formData.get('status'),
                task_type_id: formData.get('task_type')
            };

            // Validate required fields
            if (!subtaskData.task_type_id || !subtaskData.description) {
                alert('Please fill in all required fields to create a subtask.');
                return;
            }

            fetch(`/tasks/create_subtask`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': formData.get('csrf_token')
                },
                body: JSON.stringify(subtaskData)
            })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(data => {
                            throw new Error(data.message || 'Failed to create subtask');
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    // Close the modal
                    $('#taskModal').modal('hide');
                    // Show success toast
                    $('#successToast').toast('show');
                    // Optionally, refresh the related tasks section or append the new subtask to the table
                    appendNewSubtaskToTable(data.subtask);
                })
                .catch(error => {
                    console.error(error);
                    $('#errorToast').toast('show');
                });
        } else {
            // Updating the status only
            const statusData = {
                status_id: formData.get('status')
            };

            fetch(`/tasks/update/${taskId}`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': formData.get('csrf_token'),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(statusData)
            })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(data => {
                            throw new Error(data.message || 'Failed to update status');
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
                    updateTaskRow(taskId, data.new_status);
                })
                .catch(error => {
                    console.error(error);
                    $('#errorToast').toast('show');
                });
        }
    });

    // Function to append the new subtask to the table
    function appendNewSubtaskToTable(subtask) {
        // Assuming you have a table with tbody id="tasksTableBody"
        const newRow = `
            <tr id="task-row-${subtask.id}">
                <td class="d-none d-md-table-cell">${subtask.id}</td>
                <td>${subtask.task_type.division.name}</td>
                <td>${subtask.task_type.name}</td>
                <td>
                    <span class="badge bg-${subtask.status.bootstrap_class} text-capitalize"
                          id="task-status-${subtask.id}">
                        ${subtask.status.name}
                    </span>
                </td>
                <td class="text-truncate" style="max-width: 150px;" title="${subtask.description}">
                    ${subtask.description}
                </td>
                <td class="d-none d-md-table-cell">${subtask.created_user.name || 'უცნობი'}</td>
                <td class="d-none d-md-table-cell">${subtask.created_at}</td>
                <td>
                    <div class="btn-group btn-group-sm" role="group" aria-label="Actions">
                        <button class="btn btn-primary" title="ნახვა" data-toggle="modal"
                                data-target="#taskModal"
                                onclick="showTaskDetails(${subtask.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <a href="#" class="btn btn-warning" data-toggle="modal"
                           data-target="#accountTransfer"
                           onclick="accountTransfer(${subtask.id})" title="ტრანსფერი">
                            <i class="fas fa-random"></i>
                        </a>
                    </div>
                </td>
            </tr>
        `;
        $('#tasksTableBody').append(newRow);
    }

    // Function to update the task row in the table
    function updateTaskRow(taskId, newStatus) {
        const $statusCell = $(`#task-status-${taskId}`);
        if ($statusCell.length) {
            $statusCell.text(newStatus.name);
            $statusCell.removeClass().addClass(`badge bg-${newStatus.bootstrap_class} text-capitalize`);
        }
    }
});

// Function to show task details in the modal
function showTaskDetails(taskId) {
    // Reset modal content
    $('#taskDetailsContent').hide();
    $('#errorMessage').hide();
    $('#loadingSpinner').show();
    $('#actionType').val('update_status'); // Reset action type

    fetch(`/tasks/details/${taskId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load task details');
            }
            return response.json();
        })
        .then(data => {
            // Populate modal fields
            $('#taskId').text(data.id);
            $('#taskDivision').text(data.division ? data.division.name : 'არ არის მითითებული');
            $('#taskCurrentStatus').text(data.current_status.name || 'არ არის მითითებული');
            $('#taskCurrentStatus').data('status-id', data.current_status.id); // Update data attribute
            $('#taskStatus').val(data.current_status.id); // Set current status in dropdown
            $('#taskDescription').val(data.description || 'არ არის მითითებული');

            // Populate status dropdown
            const $taskStatus = $('#taskStatus');
            $taskStatus.empty();
            data.statuses.forEach(status => {
                const $option = $('<option></option>')
                    .attr('value', status.id)
                    .text(status.name);
                if (status.id === data.current_status.id) {
                    $option.prop('selected', true);
                }
                $taskStatus.append($option);
            });

            // Hide all additional fields initially
            $('#divisionSelectContainer').hide();
            $('#taskTypeContainer').hide();
            $('#taskTypeInputContainer').hide();
            $('#taskTypeSelect').html('<option value="" disabled selected>აირჩიეთ ტიპი</option>');
            $('#taskTypeInput').val('');

            // Show modal content
            $('#loadingSpinner').hide();
            $('#taskDetailsContent').fadeIn();
        })
        .catch(error => {
            console.error(error);
            $('#loadingSpinner').hide();
            $('#errorMessage').fadeIn();
        });
}
