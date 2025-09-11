document.addEventListener('DOMContentLoaded', () => {
  const userToggle = document.getElementById('user-toggle');
  const userMenu = document.getElementById('user-menu');

  if (!userToggle || !userMenu) return;

  userToggle.addEventListener('click', (e) => {
    e.stopPropagation();
    userMenu.classList.toggle('visible');
  });

  // Закрытие по клику вне меню
  document.addEventListener('click', (e) => {
    if (!userMenu.contains(e.target) && !userToggle.contains(e.target)) {
      userMenu.classList.remove('visible');
    }
  });

  // Escape клавиша — закрыть меню
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      userMenu.classList.remove('visible');
    }
  });
});
