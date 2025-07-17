document.addEventListener('DOMContentLoaded', function () {
  const togglePassword = document.getElementById('togglePassword');
  const passwordInput = document.getElementById('id_password');

  if (togglePassword && passwordInput) {
    togglePassword.addEventListener('click', function () {
      const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', type);

      this.classList.toggle('bx-lock');
      this.classList.toggle('bx-lock-open-alt');
    });
  }

  const toggleOldPassword = document.getElementById('toggleOldPassword');
  const oldPasswordInput = document.getElementById('id_old_password');

  if (toggleOldPassword && oldPasswordInput) {
    toggleOldPassword.addEventListener('click', function () {
      const type = oldPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      oldPasswordInput.setAttribute('type', type);

      this.classList.toggle('bx-lock');
      this.classList.toggle('bx-lock-open-alt');
    });
  }
});
