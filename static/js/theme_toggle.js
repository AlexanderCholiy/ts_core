document.addEventListener('DOMContentLoaded', () => {
  const themes = ['light', 'dark', 'auto'];
  const themeIcon = document.getElementById('theme-icon');
  const themeToggle = document.getElementById('theme-toggle');
  const body = document.body;

  const themeIcons = {
    light: 'bx-sun',
    dark: 'bx-moon',
    auto: 'bx-desktop'
  };

  const themeTitles = {
    light: 'Светлая тема',
    dark: 'Тёмная тема',
    auto: 'Системная тема'
  };

  function applyTheme(theme) {
    body.classList.remove('light', 'dark');
    if (theme === 'light') {
      body.classList.add('light');
    } else if (theme === 'dark') {
      body.classList.add('dark');
    } else if (theme === 'auto') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      body.classList.add(prefersDark ? 'dark' : 'light');
    }

    themeIcon.className = 'bx ' + themeIcons[theme];
    themeToggle.setAttribute('data-title', themeTitles[theme]);
  }

  function nextTheme(current) {
    const index = themes.indexOf(current);
    return themes[(index + 1) % themes.length];
  }

  function getSavedTheme() {
    return localStorage.getItem('theme') || 'auto';
  }

  function setTheme(theme) {
    localStorage.setItem('theme', theme);
    applyTheme(theme);
  }

  themeToggle.addEventListener('click', () => {
    const currentTheme = getSavedTheme();
    const newTheme = nextTheme(currentTheme);
    setTheme(newTheme);
  });

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (getSavedTheme() === 'auto') {
      applyTheme('auto');
    }
  });

  applyTheme(getSavedTheme());
});