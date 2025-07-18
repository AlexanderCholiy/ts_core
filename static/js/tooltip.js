document.querySelectorAll('.tooltip').forEach(el => {
  const title = el.getAttribute('data-title');
  if (!title) return;

  const tooltip = document.createElement('div');
  tooltip.className = 'tooltip-text';
  tooltip.textContent = title;
  document.body.appendChild(tooltip); // ВАЖНО: добавляем в body, не в el!

  let showTimeout = null;

  function showTooltip() {
    tooltip.style.display = 'block';
    tooltip.style.opacity = '0';
    tooltip.style.pointerEvents = 'none';
    tooltip.style.transition = 'none';
    tooltip.style.transform = 'translateX(-50%) translateY(0)';

    const elRect = el.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();

    const spaceBelow = window.innerHeight - elRect.bottom;
    const spaceAbove = elRect.top;

    // Позиционирование по вертикали
    if (spaceBelow >= tooltipRect.height + 6) {
      tooltip.style.top = `${elRect.bottom + 6}px`;
    } else if (spaceAbove >= tooltipRect.height + 6) {
      tooltip.style.top = `${elRect.top - tooltipRect.height - 6}px`;
    } else {
      tooltip.style.top = `${elRect.bottom + 6}px`;
    }

    // Позиционирование по горизонтали с учётом края окна
    let left = elRect.left + elRect.width / 2;
    if (left + tooltipRect.width / 2 > window.innerWidth) {
      left = window.innerWidth - tooltipRect.width / 2 - 8;
    }
    if (left - tooltipRect.width / 2 < 0) {
      left = tooltipRect.width / 2 + 8;
    }

    tooltip.style.left = `${left}px`;
    tooltip.style.transform = `translateX(-50%) translateY(0)`;

    setTimeout(() => {
      tooltip.style.transition = 'opacity 0.2s ease-in-out, transform 0.2s ease-in-out';
      tooltip.style.opacity = '1';
      tooltip.style.pointerEvents = 'auto';
    }, 10);
  }

  el.addEventListener('mouseenter', () => {
    showTimeout = setTimeout(showTooltip, 1000);
  });

  el.addEventListener('mouseleave', () => {
    clearTimeout(showTimeout);
    showTimeout = null;
    tooltip.style.opacity = '0';
    tooltip.style.pointerEvents = 'none';
    setTimeout(() => {
      tooltip.style.display = 'none';
    }, 300);
  });
});
