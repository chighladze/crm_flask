document.addEventListener('DOMContentLoaded', function () {
    // Используем jQuery для выборки элементов
    const $taskStatus = $('#taskStatus');
    const $addButton = $('#addButton');
    const $taskCurrentStatusElement = $('#taskCurrentStatus');
    const $divisionSelectContainer = $('#divisionSelectContainer');
    const $divisionSelect = $('#divisionSelect');
    const $taskTypeSelect = $('#taskTypeSelect');
    const $taskTypeContainer = $('#taskTypeContainer');
    const $taskTypeInputContainer = $('#taskTypeInputContainer');
    const $taskTypeInput = $('#taskTypeInput');

    let initialStatus;

    // Функция для установки начального статуса и скрытия всех дополнительных полей
    function setInitialStatus() {
        initialStatus = $taskCurrentStatusElement.data('status-id');
        $addButton.hide();
        $divisionSelectContainer.hide(); // Скрыть выбор дивизии при открытии модального окна
        $taskTypeContainer.hide(); // Скрыть выбор типа задачи
        $taskTypeInputContainer.hide(); // Скрыть поле ввода описания задачи
        $taskTypeSelect.html('<option value="" disabled selected>აირჩიეთ ტიპი</option>'); // Сброс типов задач
        $taskTypeInput.val(''); // Сброс текстового поля
    }

    // Обработчик изменения статуса задачи
    $taskStatus.on('change', function () {
        if ($(this).val() !== initialStatus) {
            $addButton.fadeIn(); // Плавно показать кнопку "+"
        } else {
            $addButton.fadeOut(); // Плавно скрыть кнопку "+"
            $divisionSelectContainer.slideUp(); // Плавно скрыть выбор дивизии
            $taskTypeContainer.slideUp(); // Плавно скрыть выбор типа задачи
            $taskTypeInputContainer.slideUp(); // Плавно скрыть поле ввода описания задачи
        }
    });

    // Функция для получения дивизий с сервера
    function fetchDivisions() {
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

    // Функция для заполнения выпадающего списка дивизий
    function populateDivisionSelect(divisions) {
        // Очистить существующие опции, кроме первой
        $divisionSelect.html('<option value="" disabled selected>განყოფილების არჩევა</option>');
        divisions.forEach(division => {
            const option = $('<option></option>').attr('value', division.id).text(division.name);
            $divisionSelect.append(option);
        });
    }

    // Обработчик клика по кнопке "+"
    $addButton.on('click', function () {
        // Получить дивизии с сервера
        fetchDivisions()
            .then(divisions => {
                if (divisions.length === 0) {
                    alert('No divisions available.');
                    return;
                }
                populateDivisionSelect(divisions);
                $divisionSelectContainer.slideDown(); // Плавно показать выбор дивизии
            })
            .catch(error => {
                console.error('Error fetching divisions:', error);
                alert('Failed to load divisions. Please try again later.');
            });
    });

    // Обработчик изменения выбора дивизии для загрузки типов задач
    $divisionSelect.on('change', function () {
        const selectedDivisionId = $(this).val();
        if (selectedDivisionId) {
            fetchTaskTypes(selectedDivisionId)
                .then(taskTypes => {
                    populateTaskTypeSelect(taskTypes);
                    $taskTypeContainer.slideDown(); // Плавно показать выбор типа задачи
                })
                .catch(error => {
                    console.error('Error fetching task types:', error);
                    alert('Failed to load task types. Please try again later.');
                });
        } else {
            $taskTypeSelect.html('<option value="" disabled selected>აირჩიეთ ტიპი</option>');
            $taskTypeContainer.slideUp(); // Плавно скрыть выбор типа задачи
            $taskTypeInputContainer.slideUp(); // Плавно скрыть поле ввода описания задачи
            $taskTypeInput.val('');
        }
    });

    // Функция для получения типов задач для выбранной дивизии с сервера
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
        // Очистить существующие опции, кроме первой
        $taskTypeSelect.html('<option value="" disabled selected>აირჩიეთ ტიპი</option>');
        taskTypes.forEach(taskType => {
            const option = $('<option></option>').attr('value', taskType.id).text(taskType.name);
            $taskTypeSelect.append(option);
        });
        $taskTypeInputContainer.slideUp(); // Плавно скрыть поле ввода описания задачи
        $taskTypeInput.val(''); // Сброс текстового поля
    }

    // Обработчик изменения выбора типа задачи для отображения/скрытия поля ввода описания
    $taskTypeSelect.on('change', function () {
        if ($(this).val()) {
            $taskTypeInputContainer.slideDown(); // Плавно показать поле ввода описания
        } else {
            $taskTypeInputContainer.slideUp(); // Плавно скрыть поле ввода описания
            $taskTypeInput.val(''); // Сброс текстового поля
        }
    });

    // Инициализация модального окна при его открытии
    $('#taskModal').on('show.bs.modal', function () {
        setInitialStatus(); // Установить начальный статус при открытии модального окна
    });
});

// Функция для отображения деталей задачи в модальном окне
function showTaskDetails(taskId) {
    // Сбросить содержимое модального окна
    $('#taskDetailsContent').hide();
    $('#errorMessage').hide();
    $('#loadingSpinner').show();

    fetch(`/tasks/details/${taskId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load task details');
            }
            return response.json();
        })
        .then(data => {
            // Заполнить данные задачи
            $('#taskId').text(data.id);
            $('#taskDivision').text(data.division ? data.division.name : 'არ არის მითითებული');
            $('#taskCurrentStatus').text(data.current_status.name || 'არ არის მითითებული');
            $('#taskDescription').val(data.description || 'არ არის მითითებული');

            // Заполнить выпадающий список статусов
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

            // Заполнить тип задачи на основе дивизии
            const $taskTypeSelect = $('#taskTypeSelect');
            const $taskTypeContainer = $('#taskTypeContainer');
            const $taskTypeInputContainer = $('#taskTypeInputContainer');
            const $taskTypeInput = $('#taskTypeInput');

            $taskTypeSelect.html('<option value="" disabled selected>აირჩიეთ ტიპი</option>');
            $taskTypeInput.val('');
            $taskTypeContainer.slideUp();
            $taskTypeInputContainer.slideUp();

            if (data.division && data.division.id) {
                fetch(`/tasks/task_types/get_task_types/${data.division.id}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Failed to fetch task types');
                        }
                        return response.json();
                    })
                    .then(taskTypes => {
                        taskTypes.task_types.forEach(taskType => {
                            const $option = $('<option></option>')
                                .attr('value', taskType.id)
                                .text(taskType.name);
                            if (taskType.id === data.task_type.id) {
                                $option.prop('selected', true);
                                // Показать поле ввода описания задачи, если тип уже выбран
                                $taskTypeInputContainer.slideDown();
                                $taskTypeInput.val(data.task_type_description || '');
                            }
                            $taskTypeSelect.append($option);
                        });
                        if (taskTypes.task_types.length > 0) {
                            $taskTypeContainer.slideDown(); // Показать выбор типа задачи
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching task types:', error);
                        alert('Failed to load task types. Please try again later.');
                    });
            }

            // Показать содержимое и скрыть индикатор загрузки
            $('#loadingSpinner').hide();
            $('#taskDetailsContent').fadeIn(); // Плавно показать содержимое
        })
        .catch(error => {
            console.error(error);
            $('#loadingSpinner').hide();
            $('#errorMessage').fadeIn(); // Плавно показать сообщение об ошибке
        });
}

// Обработчик отправки формы для обновления задачи
$('#taskEditForm').on('submit', function (event) {
    event.preventDefault();
    const taskId = $('#taskId').text();
    const formData = new FormData(this);

    // Валидация выбора дивизии, если она отображается
    const $divisionSelect = $('#divisionSelect');
    const selectedDivisionId = $divisionSelect.val();

    // Валидация выбора типа задачи
    const $taskTypeSelect = $('#taskTypeSelect');
    const selectedTaskTypeId = $taskTypeSelect.val();

    // Валидация описания типа задачи
    const $taskTypeInput = $('#taskTypeInput');
    const taskTypeDescription = $taskTypeInput.val().trim();

    // Проверка, выбран ли дивизия, если выбор отображается
    if ($divisionSelect.is(':visible') && !selectedDivisionId) {
        alert('Please select a division.');
        return;
    }

    // Проверка, выбран ли тип задачи, если выбор отображается
    if ($taskTypeSelect.is(':visible') && !selectedTaskTypeId) {
        alert('Please select a task type.');
        return;
    }

    // Проверка, введено ли описание задачи, если поле отображается
    if ($taskTypeSelect.is(':visible') && !taskTypeDescription) {
        alert('Please provide a description for the task type.');
        return;
    }

    // Добавляем описание типа задачи в FormData
    formData.append('task_type_description', taskTypeDescription);

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
            // Закрыть модальное окно
            $('#taskModal').modal('hide');
            // Показать уведомление об успешном обновлении
            $('#successToast').toast('show');
            // Обновить строку задачи в таблице
            updateTaskRow(taskId, data.new_status, data.new_division);
        })
        .catch(error => {
            console.error(error);
            // Показать уведомление об ошибке
            $('#errorToast').toast('show');
        });
});

// Функция для обновления строки задачи в таблице
function updateTaskRow(taskId, newStatus, newDivision) {
    const $statusCell = $(`#task-status-${taskId}`);
    if ($statusCell.length) {
        $statusCell.text(newStatus.name);
        $statusCell.removeClass().addClass(`badge bg-${newStatus.bootstrap_class} text-capitalize`);
    }

    const $divisionCell = $(`#task-division-${taskId}`);
    if ($divisionCell.length && newDivision) {
        $divisionCell.text(newDivision.name);
    }
}

// Функция для передачи аккаунта (реализуйте по необходимости)
function accountTransfer(taskId) {
    // Реализуйте логику передачи аккаунта здесь
    alert(`Transfer account for task ID: ${taskId}`);
}

// Инициализация уведомлений (Toast)
$(document).ready(function () {
    $('.toast').toast({ delay: 3000 });
});
