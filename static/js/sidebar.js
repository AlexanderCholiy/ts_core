document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.getElementById("sidebar");
  const toggleButton = document.getElementById("sidebar-toggle");
  const searchBar = document.getElementById("search-bar");

  const isMobile = () => window.innerWidth <= 768;

  const collapseSidebar = () => {
    sidebar.classList.add("collapsed");
    if (searchBar) searchBar.classList.add("collapsed");
  };

  const expandSidebar = () => {
    sidebar.classList.remove("collapsed");
    if (searchBar) searchBar.classList.remove("collapsed");
  };

  // Инициализация на десктопе
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
      const isCollapsed = sidebar.classList.toggle("collapsed");
      if (searchBar) searchBar.classList.toggle("collapsed", isCollapsed);
      localStorage.setItem("sidebar-collapsed", isCollapsed);
    }
  });

  // Закрытие сайдбара при клике вне (на мобилках)
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

  // При ресайзе закрываем мобильный сайдбар
  window.addEventListener("resize", () => {
    if (!isMobile()) {
      sidebar.classList.remove("mobile-open");
    }
  });

  const updateBodySidebarClass = () => {
    if (isMobile()) {
      document.body.classList.remove("sidebar-expanded", "sidebar-collapsed");
    } else {
      if (sidebar.classList.contains("collapsed")) {
        document.body.classList.add("sidebar-collapsed");
        document.body.classList.remove("sidebar-expanded");
      } else {
        document.body.classList.add("sidebar-expanded");
        document.body.classList.remove("sidebar-collapsed");
      }
    }
  };

  // Вызов при загрузке
  updateBodySidebarClass();

  // Вызов при клике по кнопке
  toggleButton.addEventListener("click", () => {
    // уже есть внутри toggle, просто добавь:
    updateBodySidebarClass();
  });

  // Вызов при ресайзе
  window.addEventListener("resize", () => {
    updateBodySidebarClass();
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const header = document.getElementById("header");
  const sidebarContent = document.querySelector(".sidebar-content");

  const headerHeight = header.offsetHeight;

  const observer = new IntersectionObserver(
    ([entry]) => {
      const ratio = entry.intersectionRatio; // от 0 до 1
      const offset = headerHeight * ratio;
      sidebarContent.style.marginTop = `${offset}px`;
    },
    {
      root: null,
      threshold: Array.from({ length: 101 }, (_, i) => i / 100), // 0.00, 0.01, ..., 1.00
    }
  );

  if (header) {
    observer.observe(header);
  }
});