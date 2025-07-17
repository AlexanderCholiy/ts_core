setTimeout(() => {
  const message = document.querySelector('.message');
  message.classList.add('message--hidden');
  setTimeout(() => message.remove(), 500);
}, 3000);