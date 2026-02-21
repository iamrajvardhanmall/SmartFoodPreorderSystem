
document.addEventListener('DOMContentLoaded', function () {

  const slotSelect    = document.getElementById('id_time_slot');
  const slotInfoDiv   = document.getElementById('slotInfo');
  const progressBar   = document.getElementById('slotProgressBar');
  const slotInfoText  = document.getElementById('slotInfoText');
  const submitBtn     = document.querySelector('#orderForm button[type="submit"]');
  const pricePreview  = document.getElementById('pricePreview');
  const priceText     = document.getElementById('priceText');
  const foodSelect    = document.getElementById('id_food_item');
  const quantityInput = document.querySelector('input[name="quantity"]');
  const stallFilter   = document.getElementById('stallFilter');
  const allFoodOptions = foodSelect
    ? Array.from(foodSelect.options).filter(o => o.value !== '')
    : [];

  function filterFoodByStall() {
    if (!stallFilter || !foodSelect) return;
    const selectedStallId = parseInt(stallFilter.value);

    Array.from(foodSelect.options)
      .filter(o => o.value !== '')
      .forEach(o => foodSelect.removeChild(o));

    allFoodOptions.forEach(opt => {
      const itemId = parseInt(opt.value);
      const item   = (typeof FOOD_ITEMS_JS !== 'undefined')
        ? FOOD_ITEMS_JS.find(f => f.id === itemId)
        : null;

      if (!selectedStallId || !item || item.stall_id === selectedStallId) {
        foodSelect.appendChild(opt);
      }
    });

    foodSelect.value = '';
    updatePricePreview();
  }

  if (stallFilter) {
    stallFilter.addEventListener('change', filterFoodByStall);
  }

  function getSlot(slotId) {
    return SLOT_DATA.find(s => s.id === parseInt(slotId));
  }

  function updateSlotInfo() {
    const selectedSlotId = slotSelect.value;
    if (!selectedSlotId) {
      slotInfoDiv.classList.add('d-none');
      return;
    }

    const slot = getSlot(selectedSlotId);
    if (!slot) return;

    const pct = slot.max_capacity > 0
      ? Math.round((slot.current_orders / slot.max_capacity) * 100)
      : 100;

    const remaining = slot.max_capacity - slot.current_orders;

    progressBar.style.width = pct + '%';
    progressBar.className = 'progress-bar';
    if (pct >= 100) {
      progressBar.classList.add('bg-danger');
    } else if (pct >= 70) {
      progressBar.classList.add('bg-warning');
    } else {
      progressBar.classList.add('bg-success');
    }

    if (pct >= 100) {
      slotInfoText.innerHTML =
        '<span class="text-danger fw-semibold">🚫 This slot is full. Please choose another.</span>';
      submitBtn.disabled = true;
      submitBtn.textContent = 'Slot Full — Choose Another';
    } else if (pct >= 70) {
      slotInfoText.innerHTML =
        `<span class="text-warning fw-semibold">⚡ High Demand — only ${remaining} spot(s) left.</span>`;
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="bi bi-check-circle"></i> Confirm Order';
    } else {
      slotInfoText.innerHTML =
        `<span class="text-success">${remaining} spot(s) available (${pct}% full)</span>`;
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="bi bi-check-circle"></i> Confirm Order';
    }

    slotInfoDiv.classList.remove('d-none');
  }

  function updatePricePreview() {
    const qty = parseInt(quantityInput ? quantityInput.value : 1) || 1;
    if (foodSelect && foodSelect.value) {
      pricePreview.classList.remove('d-none');
      priceText.textContent = `${qty} × selected item`;
    } else {
      pricePreview.classList.add('d-none');
    }
  }
  if (slotSelect) {
    slotSelect.addEventListener('change', updateSlotInfo);
    updateSlotInfo();   // Run on page load (in case a slot is pre-selected)
  }

  if (quantityInput) {
    quantityInput.addEventListener('input', updatePricePreview);
  }
  if (foodSelect) {
    foodSelect.addEventListener('change', updatePricePreview);
    updatePricePreview();
  }
});
