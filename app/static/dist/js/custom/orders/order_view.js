// file_path: crm_flask/app/static/dist/js/orders/order_view.js
document.addEventListener('DOMContentLoaded', function () {
    // Используем jQuery для выбора элементов
    const $taskStatus = $('#taskStatus');
    const $taskTypeSelect = $('#taskTypeSelect');
    const $addButton = $('#addButton');
    const $taskCurrentStatusElement = $('#taskCurrentStatus');
    const $divisionSelectContainer = $('#divisionSelectContainer');
    const $divisionSelect = $('#divisionSelect');
    const $taskTypeContainer = $('#taskTypeContainer');
    const $taskTypeInputContainer = $('#taskTypeInputContainer');
    const $taskTypeInput = $('#taskTypeInput');
    const $macAddressContainer = $('#macAddressContainer');
    const $macAddressInput = $('#macAddress');
    const $submitButton = $('#submitTaskButton');
    const $actionType = $('#actionType');

    let initialStatus;
    let isCreatingSubtask = false; // Флаг для отслеживания нажатия "+"

    // Функция для установки начального статуса и скрытия дополнительных полей
    function setInitialStatus() {
        initialStatus = $taskCurrentStatusElement.data('status-id');
        $addButton.hide();
        isCreatingSubtask = false; // Сбрасываем флаг
        $actionType.val('update_status'); // Действие по умолчанию

        // Скрываем все дополнительные поля
        $divisionSelectContainer.hide();
        $taskTypeContainer.hide();
        $taskTypeInputContainer.hide();
        $macAddressContainer.hide();
        $taskTypeSelect.html('<option value="" disabled selected>აირჩიეთ ტიპი</option>');
        $taskTypeInput.val('');
        $macAddressInput.val('');
        $submitButton.prop('disabled', false); // Включаем кнопку отправки
    }

    // Функция для проверки формата MAC-адреса
    function isValidMacAddress(mac) {
        const macRegex = /^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$/;
        return macRegex.test(mac);
    }

    // Обработка изменения статуса
    $taskStatus.on('change', function () {
        const selectedStatus = parseInt($(this).val());
        const selectedTaskType = parseInt($taskTypeSelect.val()) || 0;

        if (selectedStatus !== initialStatus) {
            $addButton.fadeIn(); // Показываем кнопку "+"
        } else {
            $addButton.fadeOut(); // Скрываем кнопку "+"
            // Сбрасываем действие, если статус вернулся к начальному
            isCreatingSubtask = false;
            $actionType.val('update_status');
            // Скрываем дополнительные поля
            $divisionSelectContainer.slideUp();
            $taskTypeContainer.slideUp();
            $taskTypeInputContainer.slideUp();
            $macAddressContainer.slideUp();
            $taskTypeSelect.html('<option value="" disabled selected>აირჩიეთ ტიპი</option>');
            $taskTypeInput.val('');
            $macAddressInput.val('');
            $submitButton.prop('disabled', false);
        }

        // Проверка условий для отображения поля MAC-адреса
        if (selectedStatus === 3 && selectedTaskType === 3) {
            $macAddressContainer.slideDown();
            // Проверяем наличие значения в поле MAC-адреса
            const macValue = $macAddressInput.val().trim();
            if (macValue === '') {
                $submitButton.prop('disabled', true);
            }
        } else {
            $macAddressContainer.slideUp();
            $macAddressInput.val('');
            $submitButton.prop('disabled', false);
        }
    });

    // Обработка изменения типа задачи
    $taskTypeSelect.on('change', function () {
        const selectedTaskType = parseInt($(this).val());
        const selectedStatus = parseInt($taskStatus.val());

        if (selectedStatus === 3 && selectedTaskType === 3) {
            $macAddressContainer.slideDown();
            const macValue = $macAddressInput.val().trim();
            if (macValue === '') {
                $submitButton.prop('disabled', true);
            }
        } else {
            $macAddressContainer.slideUp();
            $macAddressInput.val('');
            $submitButton.prop('disabled', false);
        }
    });

    // Обработка ввода в поле MAC-адреса
    $macAddressInput.on('input', function () {
        const macValue = $(this).val().trim();
        if (isValidMacAddress(macValue)) {
            $submitButton.prop('disabled', false);
            // Добавляем визуальное подтверждение валидности
            $(this).removeClass('is-invalid').addClass('is-valid');
        } else {
            $submitButton.prop('disabled', true);
            // Визуальное оповещение о некорректном формате
            if (macValue === '') {
                $(this).removeClass('is-invalid is-valid');
            } else {
                $(this).removeClass('is-valid').addClass('is-invalid');
            }
        }
    });

    // Обработка нажатия на кнопку "+"
    $addButton.on('click', function () {
        isCreatingSubtask = true; // Устанавливаем флаг
        $actionType.val('create_subtask'); // Обновляем тип действия

        // Получаем ID заказа из скрытого поля
        const orderId = $('#order_id').val();

        // Fetch и populate divisions
        fetchDivisions()
            .then(divisions => {
                if (divisions.length === 0) {
                    alert('No divisions available.');
                    return;
                }
                populateDivisionSelect(divisions);
                $divisionSelectContainer.slideDown(); // Показываем выбор дивизиона
            })
            .catch(error => {
                console.error('Error fetching divisions:', error);
                alert('Failed to load divisions. Please try again later.');
            });
    });

    // Функция для получения дивизионов с сервера
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

    // Функция для заполнения выпадающего списка дивизионов
    function populateDivisionSelect(divisions) {
        $divisionSelect.html('<option value="" disabled selected>განყოფილების არჩევა</option>');
        divisions.forEach(division => {
            const option = $('<option></option>').attr('value', division.id).text(division.name);
            $divisionSelect.append(option);
        });
    }

    // Обработка выбора дивизиона для получения типов задач
    $divisionSelect.on('change', function () {
        const selectedDivisionId = $(this).val();
        if (selectedDivisionId) {
            fetchTaskTypes(selectedDivisionId)
                .then(taskTypes => {
                    populateTaskTypeSelect(taskTypes);
                    $taskTypeContainer.slideDown(); // Показываем выбор типа задачи
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

    // Функция для получения типов задач на основе дивизиона
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

    // Функция для заполнения выпадающего списка типов задач
    function populateTaskTypeSelect(taskTypes) {
        $taskTypeSelect.html('<option value="" disabled selected>აირჩიეთ ტიპი</option>');
        taskTypes.forEach(taskType => {
            const option = $('<option></option>').attr('value', taskType.id).text(taskType.name);
            $taskTypeSelect.append(option);
        });
        $taskTypeInputContainer.slideUp();
        $taskTypeInput.val('');
    }

    // Обработка выбора типа задачи для отображения поля описания
    $taskTypeSelect.on('change', function () {
        if ($(this).val()) {
            $taskTypeInputContainer.slideDown(); // Показываем поле описания
        } else {
            $taskTypeInputContainer.slideUp(); // Скрываем поле описания
            $taskTypeInput.val('');
        }
    });

    // Инициализация модального окна при показе
    $('#taskModal').on('show.bs.modal', function () {
        setInitialStatus(); // Сбрасываем форму
    });

    // Обработка отправки формы
    $('#taskEditForm').on('submit', function (event) {
        event.preventDefault();
        const taskId = $('#taskId').text();
        const formData = new FormData(this);

        if (isCreatingSubtask) {
            const subtaskData = {
                parent_task_id: taskId,
                description: formData.get('task_type_description'),
                status_id: formData.get('status'),
                task_type_id: formData.get('task_type'),
                order_id: formData.get('order_id'),
                mac_address: formData.get('mac_address') // Добавляем MAC-адрес
            };

            // Проверка обязательных полей
            if (!subtaskData.task_type_id || !subtaskData.description || (subtaskData.status_id == 3 && subtaskData.task_type_id == 3 && !subtaskData.mac_address)) {
                alert('Please fill in all required fields to create a subtask.');
                return;
            }

            // Если статус и тип задачи требуют MAC-адрес
            if (subtaskData.status_id == 3 && subtaskData.task_type_id == 3) {
                if (!isValidMacAddress(subtaskData.mac_address)) {
                    alert('Please enter a valid MAC address in the format XX:XX:XX:XX:XX:XX.');
                    return;
                }
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
                    console.log('Subtask created:', data);
                    $('#taskModal').modal('hide');
                    $('body').removeClass('modal-open');
                    $('.modal-backdrop').remove();
                    $('#successToast').toast('show');

                    // Обновляем статус родительской задачи
                    updateTaskRow(data.parent_task.id, data.parent_task.status);

                    // Добавляем новую подзадачу в таблицу
                    appendNewSubtaskToTable(data.subtask);
                })
                .catch(error => {
                    console.error(error);
                    $('#taskModal').modal('hide');
                    $('body').removeClass('modal-open');
                    $('.modal-backdrop').remove();
                    $('#errorToast').toast('show');
                });
        } else {
            const statusData = {status_id: formData.get('status')};
            const taskTypeId = parseInt($taskTypeSelect.val()) || 0;

            // Если статус и тип задачи требуют MAC-адрес
            if (statusData.status_id == 3 && taskTypeId == 3) {
                const macAddress = formData.get('mac_address').trim();
                if (!macAddress) {
                    alert('MAC-მისამართი აუცილებელია ამ სტატუსისა და ტიპის დავალებისთვის.');
                    return;
                }
                if (!isValidMacAddress(macAddress)) {
                    alert('გთხოვთ, შეიყვანოთ სწორი MAC-მისამართი ფორმატში XX:XX:XX:XX:XX:XX.');
                    return;
                }
                statusData.mac_address = macAddress;
            }

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
                    console.log('Status updated:', data);
                    $('#taskModal').modal('hide');
                    $('body').removeClass('modal-open');
                    $('.modal-backdrop').remove();
                    $('#successToast').toast('show');
                    updateTaskRow(taskId, data.new_status);
                })
                .catch(error => {
                    console.error(error);
                    $('#taskModal').modal('hide');
                    $('body').removeClass('modal-open');
                    $('.modal-backdrop').remove();
                    $('#errorToast').toast('show');
                });
        }
    });

    // Функция для добавления новой подзадачи в таблицу
    function appendNewSubtaskToTable(subtask) {
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
                <td class="d-none d-md-table-cell">${subtask.created_user.name || 'Unknown'}</td>
                <td class="d-none d-md-table-cell">${subtask.created_at}</td>
                <td>
                    <div class="btn-group btn-group-sm" role="group" aria-label="Actions">
                        <button class="btn btn-primary" title="View" data-toggle="modal"
                                data-target="#taskModal"
                                onclick="showTaskDetails(${subtask.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <a href="#" class="btn btn-warning" data-toggle="modal"
                           data-target="#accountTransfer"
                           onclick="accountTransfer(${subtask.id})" title="Transfer">
                            <i class="fas fa-random"></i>
                        </a>
                    </div>
                </td>
            </tr>
        `;
        $('#tasksTableBody').append(newRow);
    }

    // Функция для обновления строки задачи в таблице
    function updateTaskRow(taskId, newStatus) {
        const $statusCell = $(`#task-status-${taskId}`);
        if ($statusCell.length) {
            $statusCell.text(newStatus.name);
            $statusCell.removeClass().addClass(`badge bg-${newStatus.bootstrap_class} text-capitalize`);
        }
    }
});

// Функция для отображения деталей задачи в модальном окне
function showTaskDetails(taskId) {
    // Сбрасываем содержимое модального окна
    $('#taskDetailsContent').hide();
    $('#errorMessage').hide();
    $('#loadingSpinner').show();
    $('#actionType').val('update_status'); // Сбрасываем тип действия

    // Запрашиваем детали задачи с сервера
    fetch(`/tasks/details/${taskId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load task details');
            }
            return response.json();
        })
        .then(data => {
            // Заполняем поля модального окна
            $('#taskId').text(data.id);
            $('#taskDivision').text(data.task_type.division ? data.task_type.division.name : 'N/A');
            $('#taskCurrentStatus').text(data.current_status.name || 'N/A');
            $('#taskCurrentStatus').data('status-id', data.current_status.id); // Обновляем data-атрибут

            // Заполняем выпадающий список статусов
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

            // Заполняем выпадающий список типов задач
            const $taskTypeSelect = $('#taskTypeSelect');
            $taskTypeSelect.empty();
            $taskTypeSelect.append('<option value="" disabled selected>აირჩიეთ ტიპი</option>');
            data.task_types.forEach(taskType => {
                const $option = $('<option></option>')
                    .attr('value', taskType.id)
                    .text(taskType.name);
                if (taskType.id === data.task_type.id) {
                    $option.prop('selected', true);
                }
                $taskTypeSelect.append($option);
            });

            // Заполняем описание задачи
            $('#taskDescription').val(data.description || 'N/A');

            // Проверяем условия для отображения поля MAC-адреса
            if (data.current_status.id === 3 && data.task_type.id === 3) {
                $('#macAddressContainer').slideDown();
                const macValue = $('#macAddress').val().trim();
                if (macValue === '') {
                    $('#submitTaskButton').prop('disabled', true);
                }
            } else {
                $('#macAddressContainer').slideUp();
                $('#macAddress').val('');
                $('#submitTaskButton').prop('disabled', false);
            }

            // Заполняем поле MAC-адреса, если оно существует
            if (data.mac_address) {
                $('#macAddress').val(data.mac_address);
                if (isValidMacAddress(data.mac_address)) {
                    $('#macAddress').removeClass('is-invalid').addClass('is-valid');
                    $('#submitTaskButton').prop('disabled', false);
                } else {
                    $('#macAddress').removeClass('is-valid').addClass('is-invalid');
                    $('#submitTaskButton').prop('disabled', true);
                }
            } else {
                $('#macAddress').val('');
                $('#macAddress').removeClass('is-valid is-invalid');
            }

            // Показываем содержимое модального окна
            $('#loadingSpinner').hide();
            $('#taskDetailsContent').fadeIn();
        })
        .catch(error => {
            console.error(error);
            $('#loadingSpinner').hide();
            $('#errorMessage').fadeIn();
        });
}

// Функция для проверки формата MAC-адреса
function isValidMacAddress(mac) {
    const macRegex = /^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$/;
    return macRegex.test(mac);
}
