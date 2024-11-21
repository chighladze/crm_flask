document.addEventListener('DOMContentLoaded', function () {
    const footer = document.querySelector('.main-footer');
    const visualDiv = document.getElementById('visual-div');

    function updateFooterPosition() {
        if (visualDiv && visualDiv.offsetParent === null) {
            // Если visualDiv скрыт
            footer.classList.add('footer-visible');
            footer.classList.remove('footer-hidden');
        } else {
            // Если visualDiv видим
            footer.classList.add('footer-hidden');
            footer.classList.remove('footer-visible');
        }
    }

    // Инициализируем проверку при загрузке страницы
    updateFooterPosition();

    // Наблюдатель на изменения DOM
    if (visualDiv) {
        const observer = new MutationObserver(updateFooterPosition);
        observer.observe(visualDiv, { attributes: true, childList: true, subtree: true });
    }
});
