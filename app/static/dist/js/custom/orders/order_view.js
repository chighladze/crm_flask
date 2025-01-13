// file_path: crm_flask/app/static/dist/js/orders/order_view.js
document.addEventListener('DOMContentLoaded', function () {
    // Кэшируем элементы
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

    // -- Проверка валидности MAC-адреса --
    function isValidMacAddress(mac) {
        const macRegex = /^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$/;
        return macRegex.test(mac);
    }

    // -- Сброс состояния модалки --
    function resetModalState() {
        isCreatingSubtask = false;
        $actionType.val('update_status');
        $subTaskCreate.hide();
        $subTaskDivisionContainer.hide();
        $subTaskTypeContainer.hide();
        $subTaskDescriptionContainer.hide();
        $subTaskDivisionId.html('<option value="" disabled selected>Выберите дивизион</option>');
        $subTaskTypeId.html('<option value="" disabled selected>Выберите тип задачи</option>');
        $subTaskDescriptionID.val('');
        $macAddressContainer.hide();
        $macAddressInput.val('');
        $macAddressInput.removeClass('is-invalid is-valid');
        $submitButton.prop('disabled', false);
    }

    // -- Обработка изменения статуса родительской задачи --
    $parentTaskStatusChangeID.on('change', function () {
        const newStatusId = parseInt($(this).val(), 10);
        const currentTypeId = parseInt($parentTaskTypeID.text(), 10);

        // Если статус изменился с начального, показываем кнопку создания подзадачи
        if (newStatusId !== initialStatusId) {
            $subTaskCreate.show();
        } else {
            // Возвращаемся к начальному состоянию
            $subTaskCreate.hide();
        }

        // Логика показа поля MAC, если тип = 3 и статус = 3
        if (currentTypeId === 3 && newStatusId === 3) {
            $macAddressContainer.slideDown();
            // Проверяем, есть ли введённый MAC
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

    // -- Обработка ввода в поле MAC-адреса (родительская задача) --
    $macAddressInput.on('input', function () {
        const macVal = $(this).val().trim();
        const currentTypeId = parseInt($parentTaskTypeID.text(), 10);
        const newStatusId = parseInt($parentTaskStatusChangeID.val(), 10);

        // Если мы в состоянии "тип=3 и статус=3"
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

    // -- Кнопка "плюс" для создания подзадачи --
    $subTaskCreate.on('click', function () {
        isCreatingSubtask = true;
        $actionType.val('create_subtask');
        // Открываем выбор дивизиона
        fetchDivisions()
            .then(divisions => {
                if (divisions.length === 0) {
                    alert('Нет доступных дивизионов.');
                    return;
                }
                populateSubTaskDivisionSelect(divisions);
                $subTaskDivisionContainer.slideDown();
            })
            .catch(err => {
                console.error(err);
                alert('Ошибка при загрузке дивизионов.');
            });
    });

    // -- Получить список дивизионов --
    function fetchDivisions() {
        return fetch('/tasks/get_divisions')
            .then(resp => {
                if (!resp.ok) throw new Error('Failed to fetch divisions');
                return resp.json();
            })
            .then(data => data.divisions);
    }

    // -- Заполнить select с дивизионами для подзадачи --
    function populateSubTaskDivisionSelect(divisions) {
        $subTaskDivisionId.html('<option value="" disabled selected>Выберите дивизион</option>');
        divisions.forEach(div => {
            const $option = $('<option></option>').attr('value', div.id).text(div.name);
            $subTaskDivisionId.append($option);
        });
    }

    // -- Когда выбираем дивизион подзадачи --
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
                    alert('Ошибка при загрузке типов задач.');
                });
        } else {
            // Скрываем всё ниже
            $subTaskTypeContainer.slideUp();
            $subTaskTypeId.html('<option value="" disabled selected>Выберите тип задачи</option>');
            $subTaskDescriptionContainer.slideUp();
            $subTaskDescriptionID.val('');
        }
    });

    // -- Получить типы задач по дивизиону --
    function fetchTaskTypesByDivision(divisionId) {
        return fetch(`/tasks/task_types/get_task_types/${divisionId}`)
            .then(resp => {
                if (!resp.ok) throw new Error('Failed to fetch task types');
                return resp.json();
            })
            .then(data => data.task_types);
    }

    // -- Заполняем select типов подзадачи --
    function populateSubTaskTypeSelect(taskTypes) {
        $subTaskTypeId.html('<option value="" disabled selected>Выберите тип задачи</option>');
        taskTypes.forEach(t => {
            const $option = $('<option></option>').attr('value', t.id).text(t.name);
            $subTaskTypeId.append($option);
        });
    }

    // -- Когда выбираем тип подзадачи --
    $subTaskTypeId.on('change', function () {
        const selectedTypeId = parseInt($(this).val(), 10);
        // Показываем поле описания
        if (selectedTypeId) {
            $subTaskDescriptionContainer.slideDown();
        } else {
            $subTaskDescriptionContainer.slideUp();
            $subTaskDescriptionID.val('');
        }
    });

    // -- Обработка отправки формы модального окна --
    $('#taskEditForm').on('submit', function (event) {
        event.preventDefault();
        const parentTaskId = parseInt($parentTaskID.text(), 10);
        const statusValue = parseInt($parentTaskStatusChangeID.val(), 10);
        const macAddressValue = $macAddressInput.val().trim();

        if ($actionType.val() === 'create_subtask') {
            // Создаём подзадачу
            const subtaskData = {
                parent_task_id: parentTaskId,
                description: $subTaskDescriptionID.val().trim(),
                status_id: statusValue,
                task_type_id: parseInt($subTaskTypeId.val() || '0', 10),
                order_id: $('#order_id').val(),
                mac_address: ''
            };

            // Если выбрали тип=3 и статус=3 => спрашиваем MAC
            if (subtaskData.task_type_id === 3 && subtaskData.status_id === 3) {
                // Уточним, нужно ли у подзадачи свой MAC:
                // По ТЗ: "Если тип = 3 и статус = 3, то поле MAC должно отображаться" – Но мы можем
                // сделать *отдельное* поле для подзадачи. Либо переиспользовать то же поле.
                // Для упрощения переиспользуем то же поле MAC
                if (!isValidMacAddress(macAddressValue)) {
                    // Если невалидный или пустой
                    alert('MAC-адрес обязателен и должен быть в корректном формате.');
                    return;
                }
                subtaskData.mac_address = macAddressValue;
            }

            if (!subtaskData.description) {
                alert('Введите описание подзадачи!');
                return;
            }
            if (!subtaskData.task_type_id) {
                alert('Выберите тип подзадачи!');
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
                        return response.json().then(data => { throw data; });
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
                    const msg = error.message || 'Ошибка при создании подзадачи.';
                    $errorToastBody.text(msg);
                    $('#errorToast').toast('show');
                });
        } else {
            // Обновляем статус родительской задачи
            const updateData = {
                status_id: statusValue,
                macAddress: ''
            };

            // Если у родительской задачи тип=3 и статус=3, то нужно MAC
            const currentTypeId = parseInt($parentTaskTypeID.text(), 10);
            if (currentTypeId === 3 && statusValue === 3) {
                if (!isValidMacAddress(macAddressValue)) {
                    alert('MAC-адрес обязателен и должен быть корректен (тип=3, статус=3).');
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
                        return response.json().then(data => { throw data; });
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
                    const msg = error.message || 'Ошибка при обновлении статуса.';
                    $errorToastBody.text(msg);
                    $('#errorToast').toast('show');
                });
        }
    });

    // -- Добавить новую подзадачу в таблицу --
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
                <td class="d-none d-md-table-cell">${subtask.created_user.name || 'Unknown'}</td>
                <td class="d-none d-md-table-cell">${subtask.created_at}</td>
                <td class="text-center">
                    <div class="btn-group btn-group-sm" role="group" aria-label="Actions">
                        <button class="btn btn-primary"
                                title="Просмотр"
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

    // -- Обновить строку задачи (badge статуса) --
    function updateTaskRow(taskId, newStatus) {
        const $statusCell = $(`#task-status-${taskId}`);
        if ($statusCell.length) {
            $statusCell.text(newStatus.name);
            $statusCell.removeClass().addClass(`badge bg-${newStatus.bootstrap_class} text-capitalize`);
        }
    }

    // -- Показать детали задачи в модальном окне --
    window.showTaskDetails = function (taskId) {
        // Сбросить состояние
        resetModalState();
        $('#taskDetailsContent').hide();
        $('#errorMessage').hide();
        $('#loadingSpinner').show();

fetch(`/tasks/details/${taskId}`)
    .then(resp => {
        if (!resp.ok) throw new Error('Failed to load task details');
        return resp.json();
    })
    .then(data => {
        // 1) Заполняем идентификаторы, как раньше
        $parentTaskID.text(data.id);
        $parentTaskTypeID.text(data.task_type.id || '');
        $parentTaskStatusID.text(data.current_status.id || '');

        // 2) Заполняем новые поля с названиями
        // Название подразделения
        const divisionName = data.task_type && data.task_type.division
            ? data.task_type.division.name
            : '';
        $('#parentTaskDivisionName').text(divisionName);

        // Название типа задачи
        const taskTypeName = data.task_type && data.task_type.name
            ? data.task_type.name
            : '';
        $('#parentTaskTypeName').text(taskTypeName);

        // Название статуса
        const statusName = data.current_status && data.current_status.name
            ? data.current_status.name
            : '';
        $('#parentTaskStatusName').text(statusName);

        // 3) Описание задачи
        $('#taskDescription').val(data.description || '');

        // 4) Список статусов (select)
        $parentTaskStatusChangeID.empty();
        data.statuses.forEach(st => {
            const $option = $('<option></option>').val(st.id).text(st.name);
            if (st.id === data.current_status.id) {
                $option.prop('selected', true);
            }
            $parentTaskStatusChangeID.append($option);
        });

        // 5) Если у задачи тип=3 и статус=3 => поле MAC
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

        // 6) Убираем спиннер, показываем контент
        $('#loadingSpinner').hide();
        $('#taskDetailsContent').fadeIn();
    })
    .catch(error => {
        console.error(error);
        $('#loadingSpinner').hide();
        $('#errorMessage').fadeIn();
    });

    };

    // -- Копирование PayID --
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

    // -- Инициализация Bootstrap tooltip --
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
