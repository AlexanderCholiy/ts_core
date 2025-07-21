// Все маппинги в одном месте
const FIELD_MAPPINGS = {
  // Для полей unit (AMBR)
  unit: {
    0: "bps",
    1: "Kbps", 
    2: "Mbps",
    3: "Gbps",
    4: "Tbps"
  },
  // Для полей type (Session Type)
  type: {
    1: "IPv4",
    2: "IPv6",
    3: "IPv4v6"
  },
  // Для полей emption (Pre-emption)
  emption: {
    0: "Disabled",
    1: "Enabled"
  },
  // Добавьте другие маппинги по необходимости
};

// Основная функция для обновления select-элементов
function updateSelectElements() {
  // Находим все select элементы, которые нужно обработать
  const selectsToUpdate = document.querySelectorAll(
    'select[name*="unit"], select[name*="type"], select[name*="emption"]'
  );

  selectsToUpdate.forEach(select => {
    // Определяем тип поля по имени
    const fieldType = 
      select.name.includes('unit') ? 'unit' :
      select.name.includes('type') ? 'type' : 'emption';
    
    // Сохраняем текущее значение
    const currentValue = select.value;
    
    // Обновляем текст для каждого option
    Array.from(select.options).forEach(option => {
      if (option.value && option.value !== "") {
        const intValue = parseInt(option.value);
        if (FIELD_MAPPINGS[fieldType] && FIELD_MAPPINGS[fieldType][intValue]) {
          option.textContent = FIELD_MAPPINGS[fieldType][intValue];
        }
      }
    });
    
    // Восстанавливаем выбранное значение
    if (currentValue && select.querySelector(`option[value="${currentValue}"]`)) {
      select.value = currentValue;
    }
  });
}

// Оптимизированный наблюдатель за изменениями DOM
function setupMutationObserver() {
  const form = document.querySelector('#subscriber_form');
  if (!form) return;

  let updateTimeout;
  let isUpdating = false;

  const observer = new MutationObserver((mutations) => {
    // Проверяем, есть ли релевантные изменения
    const hasRelevantChanges = mutations.some(mutation => {
      return Array.from(mutation.addedNodes).some(node => {
        // Нас интересуют только добавленные элементы
        if (node.nodeType !== Node.ELEMENT_NODE) return false;
        
        // Проверяем, содержит ли узел или его потомки нужные select'ы
        return node.matches('select[name*="unit"], select[name*="type"], select[name*="emption"]') || 
               node.querySelector('select[name*="unit"], select[name*="type"], select[name*="emption"]');
      });
    });

    // Если есть изменения и нет текущего обновления
    if (hasRelevantChanges && !isUpdating) {
      clearTimeout(updateTimeout);
      updateTimeout = setTimeout(() => {
        isUpdating = true;
        updateSelectElements();
        isUpdating = false;
      }, 100); // Дебаунсинг 100мс
    }
  });

  // Начинаем наблюдение только за формой
  observer.observe(form, {
    childList: true,
    subtree: true,
    attributes: false,
    characterData: false
  });

  return observer;
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
  // Первоначальное обновление
  updateSelectElements();
  
  // Настройка наблюдателя
  setupMutationObserver();
});