function markNestingLevels(container, level = 1) {
    if (!container) return;

    // Добавим классы к текущему элементу
    container.classList.add('json-field');
    container.classList.add(`json-level-${level}`);

    // Найдём все вложенные .jsonform-object или .jsonform-array
    const children = container.querySelectorAll(':scope > .jsonform-object, :scope > .jsonform-array');
    children.forEach(child => markNestingLevels(child, level + 1));
}

document.addEventListener('DOMContentLoaded', function () {
    if (window.djangoJSONForm) {
        document.querySelectorAll('.django-jsonform').forEach(function (el) {
            window.djangoJSONForm.init(el);

            // Дождёмся окончания рендера JSONForm
            setTimeout(() => {
                // el → .jsonform > .jsonform-object
                const rootContainer = el.querySelector('.jsonform > .jsonform-object');
                if (rootContainer) {
                    markNestingLevels(rootContainer, 1);
                }
            }, 100); // 100 мс обычно достаточно
        });
    }
});
