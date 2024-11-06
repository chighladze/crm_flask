// Обработчик события для формы
document.querySelector('#filterModal form').addEventListener('keydown', function (event) {
    // Проверяем, нажата ли клавиша 'Enter'
    if (event.key === 'Enter') {
        event.preventDefault(); // Предотвращаем стандартное поведение
        this.submit(); // Отправляем форму
    }
});

document.getElementById('resetFilters').addEventListener('click', function () {
    // Очищаем все поля ввода
    document.querySelector('input[name="search"]').value = '';
    document.querySelector('select[name="type_id"]').value = '';
    document.querySelector('input[name="start_date"]').value = '';
    document.querySelector('input[name="end_date"]').value = '';

    // Перенаправляем на страницу без фильтров
    window.location.href = "{{ url_for('customers.customers_list') }}";
});