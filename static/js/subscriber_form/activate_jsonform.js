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
