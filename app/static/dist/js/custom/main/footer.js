document.addEventListener('DOMContentLoaded', function () {
    const footer = document.querySelector('.main-footer');
    const visualDiv = document.getElementById('visual-div');

    function checkVisualDiv() {
        if (visualDiv && !visualDiv.offsetParent) {
            footer.style.transform = 'translateY(0)';
        } else {
            footer.style.transform = 'translateY(100%)';
        }
    }

    checkVisualDiv();
    const observer = new MutationObserver(checkVisualDiv);
    observer.observe(visualDiv, {attributes: true, childList: true, subtree: true});
});

