// file_path: crm_flask/app/static/dist/js/orders/order_view.js
document.addEventListener('DOMContentLoaded', function () {
    // Cache frequently accessed elements (English comments)
    const $parentTaskID = $('#parentTaskID');
    const $parentTaskTypeID = $('#parentTaskTypeID');
    const $parentTaskStatusID = $('#parentTaskStatusID');
    const $parentTaskStatusChangeID = $('#parentTaskStatusChangeID');
    const $macAddressContainer = $('#macAddressContainer');
    const $macAddressInput = $('#macAddressInput');
    const $subTaskCreate = $('#subTaskCreate');
    const $subTaskDivisionContainer = $('#subTaskDivisionContainer');
    const $subTaskDivisionId = $('#subTaskDivisionId');
    const $subTaskTypeContainer = $('#subTaskTypeContainer');
    const $subTaskTypeId = $('#subTaskTypeId');
    const $subTaskDescriptionContainer = $('#subTaskDescriptionContainer');
    const $subTaskDescriptionID = $('#subTaskDescriptionID');
    const $actionType = $('#actionType');
    const $submitButton = $('#submitTaskButton');
    const $errorToastBody = $('#errorToastBody');

    let initialStatusId = null;
    let initialTypeId = null;
    let isCreatingSubtask = false;

    // -- Validate MAC address format (English comment)
    function isValidMacAddress(mac) {
        const macRegex = /^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$/;
        return macRegex.test(mac);
    }

    // -- Reset modal state (English comment)
    function resetModalState() {
        isCreatingSubtask = false;
        $actionType.val('update_status');
        $subTaskCreate.hide();
        $subTaskDivisionContainer.hide();
        $subTaskTypeContainer.hide();
        $subTaskDescriptionContainer.hide();
        $subTaskDivisionId.html('<option value="" disabled selected>დივიზიონის არჩევა</option>');
        $subTaskTypeId.html('<option value="" disabled selected>დავალების ტიპის არჩევა</option>');
        $subTaskDescriptionID.val('');
        $macAddressContainer.hide();
        $macAddressInput.val('');
        $macAddressInput.removeClass('is-invalid is-valid');
        $submitButton.prop('disabled', false);
    }

    // -- Handle parent task status change (English comment)
    $parentTaskStatusChangeID.on('change', function () {
        const newStatusId = parseInt($(this).val(), 10);
        const currentTypeId = parseInt($parentTaskTypeID.text(), 10);

        // Show subtask creation button if status has changed
        if (newStatusId !== initialStatusId) {
            $subTaskCreate.show();
        } else {
            $subTaskCreate.hide();
        }

        // Show MAC address field if task_type=3 and status=3
        if (currentTypeId === 3 && newStatusId === 3) {
            $macAddressContainer.slideDown();
            const macVal = $macAddressInput.val().trim();
            if (!isValidMacAddress(macVal)) {
                $submitButton.prop('disabled', true);
            }
        } else {
            $macAddressContainer.slideUp();
            $macAddressInput.val('');
            $macAddressInput.removeClass('is-valid is-invalid');
            $submitButton.prop('disabled', false);
        }
    });

    // -- Handle MAC address input (for parent task) (English comment)
    $macAddressInput.on('input', function () {
        const macVal = $(this).val().trim();
        const currentTypeId = parseInt($parentTaskTypeID.text(), 10);
        const newStatusId = parseInt($parentTaskStatusChangeID.val(), 10);

        // Check if we are in state "task_type=3 and status=3"
        if (currentTypeId === 3 && newStatusId === 3) {
            if (isValidMacAddress(macVal)) {
                $(this).removeClass('is-invalid').addClass('is-valid');
                $submitButton.prop('disabled', false);
            } else {
                if (macVal === '') {
                    $(this).removeClass('is-valid is-invalid');
                } else {
                    $(this).removeClass('is-valid').addClass('is-invalid');
                }
                $submitButton.prop('disabled', true);
            }
        }
    });

    // -- "Plus" button for creating subtask
    $subTaskCreate.on('click', function () {
        isCreatingSubtask = true;
        $actionType.val('create_subtask');
        // Fetch divisions when user wants to create a subtask
        fetchDivisions()
            .then(divisions => {
                if (divisions.length === 0) {
                    alert('დივიზიონები ვერ მოიძებნა.');
                    return;
                }
                populateSubTaskDivisionSelect(divisions);
                $subTaskDivisionContainer.slideDown();
            })
            .catch(err => {
                console.error(err);
                alert('დივიზიონების ჩატვირთვის შეცდომა.');
            });
    });

    // -- Fetch list of divisions (English comment)
    function fetchDivisions() {
        return fetch('/tasks/get_divisions')
            .then(resp => {
                if (!resp.ok) throw new Error('Failed to fetch divisions');
                return resp.json();
            })
            .then(data => data.divisions);
    }

    // -- Populate division <select> for subtask
    function populateSubTaskDivisionSelect(divisions) {
        $subTaskDivisionId.html('<option value="" disabled selected>დივიზიონის არჩევა</option>');
        divisions.forEach(div => {
            const $option = $('<option></option>').attr('value', div.id).text(div.name);
            $subTaskDivisionId.append($option);
        });
    }

    // -- Handle division selection for subtask
    $subTaskDivisionId.on('change', function () {
        const divisionId = parseInt($(this).val(), 10);
        if (divisionId) {
            fetchTaskTypesByDivision(divisionId)
                .then(taskTypes => {
                    populateSubTaskTypeSelect(taskTypes);
                    $subTaskTypeContainer.slideDown();
                })
                .catch(err => {
                    console.error(err);
                    alert('დავალების ტიპების ჩატვირთვის შეცდომა.');
                });
        } else {
            $subTaskTypeContainer.slideUp();
            $subTaskTypeId.html('<option value="" disabled selected>დავალების ტიპის არჩევა</option>');
            $subTaskDescriptionContainer.slideUp();
            $subTaskDescriptionID.val('');
        }
    });

    // -- Fetch task types by division
    function fetchTaskTypesByDivision(divisionId) {
        return fetch(`/tasks/task_types/get_task_types/${divisionId}`)
            .then(resp => {
                if (!resp.ok) throw new Error('Failed to fetch task types');
                return resp.json();
            })
            .then(data => data.task_types);
    }

    // -- Populate <select> for subtask types
    function populateSubTaskTypeSelect(taskTypes) {
        $subTaskTypeId.html('<option value="" disabled selected>დავალების ტიპის არჩევა</option>');
        taskTypes.forEach(t => {
            const $option = $('<option></option>').attr('value', t.id).text(t.name);
            $subTaskTypeId.append($option);
        });
    }

    // -- Handle subtask type selection
    $subTaskTypeId.on('change', function () {
        const selectedTypeId = parseInt($(this).val(), 10);
        // Show description field for subtask
        if (selectedTypeId) {
            $subTaskDescriptionContainer.slideDown();
        } else {
            $subTaskDescriptionContainer.slideUp();
            $subTaskDescriptionID.val('');
        }
    });

    // -- Handle form submission in the modal
    $('#taskEditForm').on('submit', function (event) {
        event.preventDefault();
        const parentTaskId = parseInt($parentTaskID.text(), 10);
        const statusValue = parseInt($parentTaskStatusChangeID.val(), 10);
        const macAddressValue = $macAddressInput.val().trim();

        if ($actionType.val() === 'create_subtask') {
            // Creating a subtask
            const subtaskData = {
                parent_task_id: parentTaskId,
                description: $subTaskDescriptionID.val().trim(),
                status_id: statusValue,
                task_type_id: parseInt($subTaskTypeId.val() || '0', 10),
                order_id: $('#order_id').val(),
                mac_address: ''
            };

            // If type=3 and status=3 => need a MAC
            if (subtaskData.task_type_id === 3 && subtaskData.status_id === 3) {
                if (!isValidMacAddress(macAddressValue)) {
                    // Show Georgian user message
                    alert('MAC-მისამართი აუცილებელია და უნდა იყოს სწორი ფორმატის!');
                    return;
                }
                subtaskData.mac_address = macAddressValue;
            }

            if (!subtaskData.description) {
                alert('ქვეკარვის აღწერა შეავსეთ!');
                return;
            }
            if (!subtaskData.task_type_id) {
                alert('ქვეკარვის ტიპი შეარჩიეთ!');
                return;
            }

            fetch('/tasks/create_subtask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': $('input[name="csrf_token"]').val()
                },
                body: JSON.stringify(subtaskData)
            })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(data => {
                            throw data;
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    $('#taskModal').modal('hide');
                    $('#successToast').toast('show');
                    appendNewSubtaskToTable(data.subtask);
                })
                .catch(error => {
                    console.error(error);
                    const msg = error.message || 'ქვეკარვის შექმნის შეცდომა.';
                    $errorToastBody.text(msg);
                    $('#errorToast').toast('show');
                });
        } else {
            // Updating parent task status
            const updateData = {
                status_id: statusValue,
                macAddress: ''
            };

            // If parent task type=3 and status=3 => need MAC
            const currentTypeId = parseInt($parentTaskTypeID.text(), 10);
            if (currentTypeId === 3 && statusValue === 3) {
                if (!isValidMacAddress(macAddressValue)) {
                    alert('MAC-მისამართი აუცილებელია და უნდა იყოს სწორი ფორმატის (ტიპ=3, სტატუს=3)!');
                    return;
                }
                updateData.macAddress = macAddressValue;
            }

            fetch(`/tasks/update/${parentTaskId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': $('input[name="csrf_token"]').val()
                },
                body: JSON.stringify(updateData)
            })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(data => {
                            throw data;
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    $('#taskModal').modal('hide');
                    $('#successToast').toast('show');
                    updateTaskRow(parentTaskId, data.new_status);
                })
                .catch(error => {
                    console.error(error);
                    const msg = error.message || 'სტატუსის განახლების შეცდომა.';
                    $errorToastBody.text(msg);
                    $('#errorToast').toast('show');
                });
        }
    });

    // -- Append new subtask to the table (English comment)
    function appendNewSubtaskToTable(subtask) {
        const newRow = `
            <tr id="task-row-${subtask.id}">
                <td class="d-none d-md-table-cell">${subtask.id}</td>
                <td>${subtask.task_type.division ? subtask.task_type.division.name : ''}</td>
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
                <td class="text-center">
                    <div class="btn-group btn-group-sm" role="group" aria-label="Actions">
                        <button class="btn btn-primary"
                                title="ნახვა"
                                data-toggle="modal"
                                data-target="#taskModal"
                                onclick="showTaskDetails(${subtask.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
        $('#tasksTableBody').append(newRow);
    }

    // -- Update a task row to reflect new status
    function updateTaskRow(taskId, newStatus) {
        const $statusCell = $(`#task-status-${taskId}`);
        if ($statusCell.length) {
            $statusCell.text(newStatus.name);
            $statusCell.removeClass().addClass(`badge bg-${newStatus.bootstrap_class} text-capitalize`);
        }
    }

    // -- Show task details in modal window
    window.showTaskDetails = function (taskId) {
        resetModalState();
        $('#taskDetailsContent').hide();
        $('#errorMessage').hide();
        $('#loadingSpinner').show();

        fetch(`/tasks/details/${taskId}`)
            .then(resp => {
                if (!resp.ok) throw new Error('ვერ ჩაიტვირთა დავალების დეტალები');
                return resp.json();
            })
            .then(data => {
                // 1) Fill basic IDs
                $parentTaskID.text(data.id);
                $parentTaskTypeID.text(data.task_type.id || '');
                $parentTaskStatusID.text(data.current_status.id || '');

                // 2) Fill name fields
                const divisionName = data.task_type && data.task_type.division
                    ? data.task_type.division.name
                    : '';
                $('#parentTaskDivisionName').text(divisionName);

                const taskTypeName = data.task_type && data.task_type.name
                    ? data.task_type.name
                    : '';
                $('#parentTaskTypeName').text(taskTypeName);

                const statusName = data.current_status && data.current_status.name
                    ? data.current_status.name
                    : '';
                $('#parentTaskStatusName').text(statusName);

                // 3) Task description
                $('#taskDescription').val(data.description || '');

                // 4) Populate status <select>
                $parentTaskStatusChangeID.empty();
                data.statuses.forEach(st => {
                    const $option = $('<option></option>').val(st.id).text(st.name);
                    if (st.id === data.current_status.id) {
                        $option.prop('selected', true);
                    }
                    $parentTaskStatusChangeID.append($option);
                });

                // 5) Show MAC field if type=3 and status=3
                if (initialTypeId === 3 && initialStatusId === 3) {
                    $macAddressContainer.slideDown();
                    if (data.mac_address) {
                        $macAddressInput.val(data.mac_address);
                        if (isValidMacAddress(data.mac_address)) {
                            $macAddressInput.removeClass('is-invalid').addClass('is-valid');
                            $submitButton.prop('disabled', false);
                        } else {
                            $macAddressInput.removeClass('is-valid').addClass('is-invalid');
                            $submitButton.prop('disabled', true);
                        }
                    }
                } else {
                    $macAddressContainer.hide();
                    $macAddressInput.val('');
                    $macAddressInput.removeClass('is-valid is-invalid');
                }

                // 6) Hide spinner, show content
                $('#loadingSpinner').hide();
                $('#taskDetailsContent').fadeIn();
            })
            .catch(error => {
                console.error(error);
                $('#loadingSpinner').hide();
                $('#errorMessage').fadeIn();
            });
    };

    // -- Copy PayID to clipboard (English comment)
    window.copyPayID = function (button, payID) {
        const tempInput = document.createElement('textarea');
        tempInput.value = payID;
        document.body.appendChild(tempInput);
        tempInput.select();
        tempInput.setSelectionRange(0, 99999);

        try {
            const successful = document.execCommand('copy');
            if (successful) {
                const icon = button.querySelector('i');
                const originalClass = icon.className;
                icon.className = 'fas fa-check text-success';
                setTimeout(() => {
                    icon.className = originalClass;
                }, 1000);
            }
        } catch (err) {
            console.error(err);
        }
        document.body.removeChild(tempInput);
    };

    // -- Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
