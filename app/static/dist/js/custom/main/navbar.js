// Получаем элементы
const userMenuModal = document.getElementById('userMenuModal');
const openUserMenu = document.getElementById('openUserMenu');
const closeUserMenu = document.getElementById('closeUserMenu');

// Открыть модальное окно
openUserMenu.addEventListener('click', (e) => {
    e.preventDefault(); // Отмена перехода по ссылке
    userMenuModal.style.display = 'block'; // Показать окно
});

// Закрыть модальное окно
closeUserMenu.addEventListener('click', () => {
    userMenuModal.style.display = 'none'; // Скрыть окно
});

// Закрыть модальное окно при клике вне его
window.addEventListener('click', (e) => {
    if (e.target === userMenuModal) {
        userMenuModal.style.display = 'none'; // Скрыть окно
    }
});
