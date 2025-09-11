document.addEventListener('DOMContentLoaded', () => {
  const block = document.getElementById('cooloff-block');
  const elem = document.getElementById('cooloff-time');
  if (!block || !elem) return;

  const loginUrl = block.getAttribute('data-login-url') || '/login/';

  let tdStr = elem.getAttribute('data-utc'); 
  if (!tdStr) return;

  const parts = tdStr.split(':').map(Number);
  if (parts.length !== 3 || parts.some(isNaN)) return;

  let totalSeconds = parts[0] * 3600 + parts[1] * 60 + parts[2];

  function formatTime(sec) {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    if (m > 0 && s > 0) return `${m} мин ${s} сек`;
    if (m > 0) return `${m} мин`;
    return `${s} сек`;
  }

  function updateTimer() {
    if (totalSeconds <= 0) {
      block.innerHTML = `
        <a href="${loginUrl}" class="link-text">Вернуться на страницу входа</a>
      `;
      clearInterval(intervalId);
      return;
    }
    elem.textContent = formatTime(totalSeconds);
    totalSeconds--;
  }

  updateTimer();
  const intervalId = setInterval(updateTimer, 1000);
});
