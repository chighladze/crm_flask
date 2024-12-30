/* file_path: crm_flask/app/static/dist/js/custom/orders/order_view.js */
document.addEventListener('DOMContentLoaded', function () {
    const taskStatus = document.getElementById('taskStatus');
    const addButton = document.getElementById('addButton');
    const taskCurrentStatusElement = document.getElementById('taskCurrentStatus');

    let initialStatus;

    // Функция для установки начального статуса на основе содержимого taskCurrentStatus
    function setInitialStatus() {
        initialStatus = taskCurrentStatusElement.getAttribute('data-status-id'); // Получаем ID статуса из атрибута
        addButton.style.display = 'none'; // Скрываем кнопку при открытии модального окна
    }

    // Обработчик изменения значения select
    taskStatus.addEventListener('change', function () {

        if (taskStatus.value !== initialStatus) {
            // Показываем кнопку "+"
            addButton.style.display = 'inline-block';
        } else {
            // Скрываем кнопку "+"
            addButton.style.display = 'none';
        }
    });

    // Дополнительный обработчик нажатия на кнопку "+"
    addButton.addEventListener('click', function () {
        alert("Кнопка '+' нажата!");
        // Реализуй дополнительную логику здесь
    });

    // Устанавливаем обработчик открытия модального окна
    $('#taskModal').on('show.bs.modal', function () {
        setInitialStatus(); // Устанавливаем начальный статус при каждом открытии модального окна
    });
});


// Функция для отображения деталей задачи в модальном окне
function showTaskDetails(taskId) {
    // Сброс содержимого модального окна
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
            // Заполнение данных задачи
            document.getElementById('taskId').textContent = data.id;
            document.getElementById('taskDivision').textContent = data.task_type.division.name || 'არ არის მითითებული';
            document.getElementById('taskType').textContent = data.task_type.name || 'არ არის მითითებული';
            document.getElementById('taskCurrentStatus').textContent = data.current_status.name || 'არ არის მითითებული';
            document.getElementById('taskDescription').value = data.description || 'არ არის მითითებული';

            // Заполнение выпадающего списка статусов
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

            // Отображение содержимого и скрытие индикатора загрузки
            document.getElementById('loadingSpinner').style.display = 'none';
            document.getElementById('taskDetailsContent').style.display = 'block';
        })
        .catch(error => {
            console.error(error);
            document.getElementById('loadingSpinner').style.display = 'none';
            document.getElementById('errorMessage').style.display = 'block';
        });
}

// Обработчик отправки формы обновления задачи
document.getElementById('taskEditForm').addEventListener('submit', function (event) {
    event.preventDefault();
    const taskId = document.getElementById('taskId').textContent;
    const formData = new FormData(this);

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
            // Закрытие модального окна
            $('#taskModal').modal('hide');
            // Показ уведомления об успешном обновлении
            $('#successToast').toast('show');
            // Обновление статуса задачи в таблице без перезагрузки страницы
            updateTaskRow(taskId, data.new_status);
        })
        .catch(error => {
            console.error(error);
            // Показ уведомления об ошибке
            $('#errorToast').toast('show');
        });
});

// Функция для обновления строки задачи в таблице
function updateTaskRow(taskId, newStatus) {
    const statusCell = document.getElementById(`task-status-${taskId}`);
    if (statusCell) {
        statusCell.textContent = newStatus.name;
        statusCell.className = `badge bg-${newStatus.bootstrap_class} text-capitalize`;
    }
}

// Функция для передачи аккаунта (реализуйте по необходимости)
function accountTransfer(taskId) {
    // Реализуйте логику передачи аккаунта здесь
    alert(`Transfer account for task ID: ${taskId}`);
}

// Инициализация уведомлений Toast
$(document).ready(function () {
    $('.toast').toast({delay: 3000});
});