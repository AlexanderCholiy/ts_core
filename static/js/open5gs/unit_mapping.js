// Все маппинги в одном месте
const FIELD_MAPPINGS = {
  unit: {
    0: "bps",
    1: "Kbps", 
    2: "Mbps",
    3: "Gbps",
    4: "Tbps"
  },
  type: {
    1: "IPv4",
    2: "IPv6",
    3: "IPv4v6"
  },
  emption: {
    0: "Disabled",
    1: "Enabled"
  }
};

// Обновляет текст option'ов select-ов по маппингам
function updateSelectElements() {
  const selectsToUpdate = document.querySelectorAll(
    'select[name*="unit"], select[name*="type"], select[name*="emption"]'
  );

  selectsToUpdate.forEach(select => {
    const fieldType = 
      select.name.includes('unit') ? 'unit' :
      select.name.includes('type') ? 'type' : 'emption';

    const currentValue = select.value;

    Array.from(select.options).forEach(option => {
      if (option.value !== "") {
        const intValue = parseInt(option.value);
        const mapped = FIELD_MAPPINGS[fieldType]?.[intValue];
        if (mapped) option.textContent = mapped;
      }
    });

    if (currentValue) {
      select.value = currentValue;
    }
  });
}

// Скрывает поля по их title (в label)
function hideFieldsByTitle(titlesToHide = []) {
  titlesToHide.forEach(title => {
    // Скрываем по label с текстом title
    document.querySelectorAll('label').forEach(label => {
      if (label.textContent.trim() === title) {
        let container = label.closest('.rjf-form-row');
        if (container) {
          container.style.display = 'none';
        }
      }
    });

    // Скрываем по div.rjf-form-group-title с текстом title
    document.querySelectorAll('.rjf-form-group-title').forEach(div => {
      if (div.textContent.trim() === title) {
        let container = div.closest('.rjf-form-group');
        if (container) {
          container.style.display = 'none';
        }
      }
    });
  });
}


// Наблюдатель для динамических изменений формы
function setupMutationObserver() {
  const form = document.querySelector('#subscriber_form');
  if (!form) return;

  let updateTimeout;
  let isUpdating = false;

  const observer = new MutationObserver((mutations) => {
    const hasRelevantChanges = mutations.some(mutation =>
      Array.from(mutation.addedNodes).some(node =>
        node.nodeType === Node.ELEMENT_NODE &&
        (node.matches('select[name*="unit"], select[name*="type"], select[name*="emption"], label') || 
         node.querySelector?.('select[name*="unit"], select[name*="type"], select[name*="emption"], label'))
      )
    );

    if (hasRelevantChanges && !isUpdating) {
      clearTimeout(updateTimeout);
      updateTimeout = setTimeout(() => {
        isUpdating = true;
        updateSelectElements();
        // Скрываем нужные поля по title
        hideFieldsByTitle(['_id', 'Flow']);
        isUpdating = false;
      }, 100);
    }
  });

  observer.observe(form, {
    childList: true,
    subtree: true
  });

  return observer;
}

// Обработка кликов по кнопкам внутри блока id_slice_jsonform
function setupButtonClickHandler() {
  const container = document.querySelector('#id_slice_jsonform');
  if (!container) return;

  container.addEventListener('click', (event) => {
    if (event.target.tagName === 'BUTTON') {
      setTimeout(() => {
        updateSelectElements();
        hideFieldsByTitle(['_id', 'Flow']);
      }, 50);  // отложить чтобы DOM успел обновиться
    }
  });
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
  updateSelectElements();
  hideFieldsByTitle(['_id', 'Flow']);
  setupMutationObserver();
  setupButtonClickHandler();
});
