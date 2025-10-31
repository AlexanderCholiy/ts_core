function initConfirmModal({ modalId, confirmBtnId, cancelBtnId }) {
  const modal = document.getElementById(modalId);
  const confirmBtn = document.getElementById(confirmBtnId);
  const cancelBtn = document.getElementById(cancelBtnId);
  let currentForm = null;

  function open(form) {
    currentForm = form;
    modal.style.display = 'flex';
  }

  function close(resetFile = true) {
    modal.style.display = 'none';
    if (resetFile && currentForm) {
      currentForm.querySelector('input[type="file"]').value = '';
    }
  }

  cancelBtn.addEventListener('click', () => close(true));
  confirmBtn.addEventListener('click', () => {
    modal.style.display = 'none';
    currentForm.submit();
  });

  return open;
}

// Инициализация двух модалок
const confirmUpload = initConfirmModal({
  modalId: 'custom-confirm-upload',
  confirmBtnId: 'confirm-upload-btn',
  cancelBtnId: 'cancel-upload-btn',
});

const confirmDelete = initConfirmModal({
  modalId: 'custom-confirm-delete',
  confirmBtnId: 'confirm-delete-btn',
  cancelBtnId: 'cancel-delete-btn',
});
