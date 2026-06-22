/* ========================================
   SGPT — MAIN JS
   Interacciones generales
   ======================================== */

// ── Modal helpers ──
function openAddModal(projectId) {
    const modal = document.getElementById('addTaskModal');
    if (modal) {
        // Set default due date to today
        const today = new Date().toISOString().split('T')[0];
        const dueInput = document.getElementById('task-due');
        if (dueInput) dueInput.value = today;
        modal.classList.add('active');
    }
}

function closeAddModal() {
    const modal = document.getElementById('addTaskModal');
    if (modal) modal.classList.remove('active');
}

function openEditModal(taskId, title, description, dueDate, statusId, priorityId) {
    const modal = document.getElementById('editTaskModal');
    const form = document.getElementById('editTaskForm');

    document.getElementById('edit-task-title').value = title || '';
    document.getElementById('edit-task-desc').value = description || '';
    document.getElementById('edit-task-due').value = dueDate || '';

    const prioritySelect = document.getElementById('edit-task-priority');
    if (prioritySelect && priorityId) {
        prioritySelect.value = priorityId;
    }

    const statusSelect = document.getElementById('edit-task-status');
    if (statusSelect && statusId) {
        statusSelect.value = statusId;
    }

    form.action = `/tasks/${taskId}/edit`;

    if (modal) modal.classList.add('active');
}

function closeEditModal() {
    const modal = document.getElementById('editTaskModal');
    if (modal) modal.classList.remove('active');
}

// Close modals on ESC
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeAddModal();
        closeEditModal();
    }
});

// ── Sidebar toggle for mobile ──
document.addEventListener('click', function(e) {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;

    // Close sidebar when clicking outside on mobile
    if (sidebar.classList.contains('open') &&
        !sidebar.contains(e.target) &&
        !e.target.closest('.menu-toggle')) {
        sidebar.classList.remove('open');
    }
});

// ── Delete confirmation ──
document.querySelectorAll('.delete-form').forEach(function(form) {
    form.addEventListener('submit', function(e) {
        // Confirmation is handled inline via onclick, but we double-check
        if (!confirm('¿Estás seguro de que deseas eliminar este elemento?')) {
            e.preventDefault();
        }
    });
});

// ── Auto-dismiss flash messages ──
const flashes = document.querySelectorAll('.flash-message');
flashes.forEach(function(flash) {
    setTimeout(function() {
        flash.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(function() { flash.remove(); }, 300);
    }, 4000);
});

/* Add slideOut animation */
const style = document.createElement('style');
style.textContent = `
@keyframes slideOut {
    to { opacity: 0; transform: translateX(20px); }
}`;
document.head.appendChild(style);

// ── Complete task (quick toggle) ──
function completeTask(taskId) {
    fetch(`/tasks/${taskId}/toggle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.status === 'ok') {
            // Reload the page to show updated state
            location.reload();
        }
    })
    .catch(function() {
        // Fallback: just reload
        location.reload();
    });
}

// ── Disable buttons during form submission ──
document.querySelectorAll('form').forEach(function(form) {
    form.addEventListener('submit', function() {
        const btn = form.querySelector('button[type="submit"]');
        if (btn) {
            btn.disabled = true;
            btn.textContent = 'Guardando...';
            setTimeout(function() {
                btn.disabled = false;
                btn.textContent = btn.dataset.originalText || btn.textContent;
            }, 5000);
        }
    });

    // Store original text
    const btn = form.querySelector('button[type="submit"]');
    if (btn) btn.dataset.originalText = btn.textContent;
});

// ── Progress bar animation on load ──
document.querySelectorAll('.progress-fill').forEach(function(bar) {
    const width = bar.style.width;
    bar.style.width = '0';
    setTimeout(function() {
        bar.style.width = width;
    }, 100);
});