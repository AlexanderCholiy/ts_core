document.addEventListener('DOMContentLoaded', function () {
const togglePassword = document.getElementById('togglePassword');
const passwordInput = document.getElementById('id_password');

togglePassword.addEventListener('click', function () {
    const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordInput.setAttribute('type', type);

    this.classList.toggle('bx-lock');
    this.classList.toggle('bx-lock-open-alt');
});
});