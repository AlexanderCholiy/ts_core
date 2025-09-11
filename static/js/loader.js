document.addEventListener("DOMContentLoaded", () => {
  const spinnerOverlay = document.getElementById("spinner-overlay");
  const message = document.querySelector(".message");

  // Сначала скрываем загрузчик
  setTimeout(() => {
    spinnerOverlay.classList.add("hidden");

    // Только после скрытия загрузчика — запускаем таймер для скрытия сообщения
    if (message) {
      setTimeout(() => {
        message.classList.add("message--hidden");
        setTimeout(() => message.remove(), 500);
      }, 7000);
    }

  }, 200);
});