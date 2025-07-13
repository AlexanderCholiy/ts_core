document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const toggleButton = document.getElementById("sidebar-toggle");

  const isMobile = () => window.innerWidth <= 768;

  const collapseSidebar = () => sidebar.classList.add("collapsed");
  const expandSidebar = () => sidebar.classList.remove("collapsed");

  // Инициализация (только для десктопа)
  if (!isMobile()) {
    const savedState = localStorage.getItem("sidebar-collapsed");
    if (savedState === "true") {
      collapseSidebar();
    }
  }

  toggleButton.addEventListener("click", () => {
    if (isMobile()) {
      sidebar.classList.toggle("mobile-open");
    } else {
      sidebar.classList.toggle("collapsed");
      const isCollapsed = sidebar.classList.contains("collapsed");
      localStorage.setItem("sidebar-collapsed", isCollapsed);
    }
  });

  // Закрытие сайдбара при клике вне (на мобильных)
  document.addEventListener("click", (e) => {
    if (
      isMobile() &&
      sidebar.classList.contains("mobile-open") &&
      !sidebar.contains(e.target) &&
      !toggleButton.contains(e.target)
    ) {
      sidebar.classList.remove("mobile-open");
    }
  });

  // Переключение поведения при ресайзе
  window.addEventListener("resize", () => {
    if (!isMobile()) {
      sidebar.classList.remove("mobile-open");
    }
  });
});

window.addEventListener("scroll", () => {
  if (window.scrollY > 0) {
    document.body.classList.add("scrolled");
  } else {
    document.body.classList.remove("scrolled");
  }
});