document.addEventListener('DOMContentLoaded', function() {
    if (window.djangoJSONForm) {
        document.querySelectorAll('.django-jsonform').forEach(function(el) {
            window.djangoJSONForm.init(el);
        });
    }
});