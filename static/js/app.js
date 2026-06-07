/* =============================================
   GroceryFlow — app.js
   Real-time interactions via Fetch API
   ============================================= */

// ── Toggle password visibility ──────────────────
function togglePassword(inputId) {
  const input = document.getElementById(inputId);
  const iconId = inputId === 'password' ? 'toggle-pw-icon' : 'toggle-confirm-icon';
  const icon = document.getElementById(iconId) ||
               document.getElementById('toggle-password-icon');
  if (!input) return;
  if (input.type === 'password') {
    input.type = 'text';
    if (icon) { icon.classList.replace('fa-eye', 'fa-eye-slash'); }
  } else {
    input.type = 'password';
    if (icon) { icon.classList.replace('fa-eye-slash', 'fa-eye'); }
  }
}

// ── Toggle Favourite ────────────────────────────
async function toggleFavourite(listId, btn) {
  try {
    const resp = await fetch(`/list/${listId}/favourite`, {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
    });
    if (!resp.ok) throw new Error('Request failed');
    const data = await resp.json();

    const icon = btn.querySelector('i');
    if (data.is_favourite) {
      icon.classList.replace('fa-regular', 'fa-solid');
      btn.classList.add('active');
      btn.title = 'Remove from favourites';
      showToast('Added to favourites ⭐', 'success');
      // Add glow to card if on dashboard
      const card = document.getElementById(`list-card-${listId}`);
      if (card) card.classList.add('is-favourite');
    } else {
      icon.classList.replace('fa-solid', 'fa-regular');
      btn.classList.remove('active');
      btn.title = 'Add to favourites';
      showToast('Removed from favourites', 'info');
      const card = document.getElementById(`list-card-${listId}`);
      if (card) card.classList.remove('is-favourite');
    }
  } catch (err) {
    showToast('Something went wrong. Please try again.', 'error');
  }
}

// ── Toggle Item Check ───────────────────────────
async function toggleItem(itemId, btn, listId) {
  try {
    const resp = await fetch(`/item/${itemId}/toggle`, {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
    });
    if (!resp.ok) throw new Error('Request failed');
    const data = await resp.json();

    const row = document.getElementById(`item-row-${itemId}`);
    const icon = document.getElementById(`check-icon-${itemId}`);

    if (data.is_checked) {
      row.classList.add('item-checked');
      btn.classList.add('checked');
      icon.classList.replace('fa-circle', 'fa-circle-check');
    } else {
      row.classList.remove('item-checked');
      btn.classList.remove('checked');
      icon.classList.replace('fa-circle-check', 'fa-circle');
    }

    // Update progress
    updateProgress(data.progress, listId);
  } catch (err) {
    showToast('Could not update item. Please try again.', 'error');
  }
}

// ── Delete Item ─────────────────────────────────
async function deleteItem(itemId, btn) {
  if (!confirm('Remove this item from the list?')) return;
  try {
    const resp = await fetch(`/item/${itemId}/delete`, {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
    });
    if (!resp.ok) throw new Error('Request failed');
    const data = await resp.json();
    if (data.success) {
      const row = document.getElementById(`item-row-${itemId}`);
      if (row) {
        row.style.transition = 'opacity 0.3s, transform 0.3s';
        row.style.opacity = '0';
        row.style.transform = 'translateX(20px)';
        setTimeout(() => {
          row.remove();
          checkEmptyCategory();
        }, 300);
      }
      showToast('Item removed.', 'info');
    }
  } catch (err) {
    showToast('Could not delete item. Please try again.', 'error');
  }
}

// ── Update Progress Display ─────────────────────
function updateProgress(progress, listId) {
  // Progress percentage text
  const pctDisplay = document.getElementById('progress-pct-display');
  if (pctDisplay) pctDisplay.textContent = `${progress}%`;

  // SVG circle
  const circleFill = document.getElementById('circle-fill-path');
  if (circleFill) {
    const circumference = 201;
    const offset = circumference - (circumference * progress / 100);
    circleFill.setAttribute('stroke-dashoffset', offset.toFixed(2));
  }

  // Count checked items in DOM
  const checkedRows = document.querySelectorAll('.item-row.item-checked').length;
  const totalRows = document.querySelectorAll('.item-row').length;
  const countDisplay = document.getElementById('checked-count-display');
  if (countDisplay) countDisplay.textContent = checkedRows;

  // Update "/ X done" label
  const miniLabel = document.querySelector('.stat-mini-label');
  if (miniLabel) miniLabel.textContent = `/ ${totalRows} done`;
}

// ── Remove empty category groups ────────────────
function checkEmptyCategory() {
  const groups = document.querySelectorAll('.category-group');
  groups.forEach(group => {
    const items = group.querySelectorAll('.item-row');
    if (items.length === 0) {
      group.style.transition = 'opacity 0.3s';
      group.style.opacity = '0';
      setTimeout(() => group.remove(), 300);
    }
  });

  // Show empty state if no items left
  const section = document.querySelector('.items-section');
  const remainingGroups = document.querySelectorAll('.category-group');
  if (section && remainingGroups.length === 0) {
    section.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🎉</div>
        <h3 class="empty-title">All done!</h3>
        <p class="empty-desc">You've checked off everything on this list. Great shopping!</p>
      </div>`;
  }
}

// ── Toast Notifications ──────────────────────────
function showToast(message, type = 'info') {
  const icons = {
    success: 'fa-circle-check',
    error:   'fa-circle-xmark',
    info:    'fa-circle-info',
  };
  const toast = document.createElement('div');
  toast.className = `flash flash-${type}`;
  toast.innerHTML = `
    <i class="fa-solid ${icons[type] || icons.info}"></i>
    <span>${message}</span>
    <button class="flash-close" onclick="this.parentElement.remove()">
      <i class="fa-solid fa-xmark"></i>
    </button>`;

  let container = document.getElementById('flash-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'flash-container';
    container.className = 'flash-container';
    document.querySelector('.main-content').prepend(container);
  }
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.transition = 'opacity 0.4s';
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 400);
  }, 3500);
}

// ── Auto-dismiss flash messages ──────────────────
document.addEventListener('DOMContentLoaded', () => {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach((flash, i) => {
    setTimeout(() => {
      flash.style.transition = 'opacity 0.5s';
      flash.style.opacity = '0';
      setTimeout(() => flash.remove(), 500);
    }, 4000 + i * 500);
  });
});
