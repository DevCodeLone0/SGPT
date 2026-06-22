/* ========================================
   SGPT — KANBAN JS
   Tablero Kanban con drag & drop
   ======================================== */

(function() {
    // Simple drag and drop without external library
    const cards = document.querySelectorAll('.kanban-card');
    let draggedCard = null;

    cards.forEach(function(card) {
        card.setAttribute('draggable', 'false'); // Disable native drag, we use buttons
    });

    // The kanban uses status dropdown for now (simpler UX)
    // If you want real drag-and-drop, uncomment below

    /*
    cards.forEach(function(card) {
        card.addEventListener('dragstart', function(e) {
            draggedCard = this;
            this.style.opacity = '0.5';
            e.dataTransfer.effectAllowed = 'move';
        });

        card.addEventListener('dragend', function() {
            this.style.opacity = '1';
            draggedCard = null;
            document.querySelectorAll('.kanban-cards').forEach(function(col) {
                col.classList.remove('drag-over');
            });
        });
    });

    document.querySelectorAll('.kanban-cards').forEach(function(col) {
        col.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            this.classList.add('drag-over');
        });

        col.addEventListener('dragleave', function() {
            this.classList.remove('drag-over');
        });

        col.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            if (draggedCard) {
                this.insertBefore(draggedCard, this.querySelector('.kanban-add-card'));
                // Trigger status change via fetch
                const taskId = draggedCard.dataset.taskId;
                const newStatusId = this.dataset.statusId;
                if (taskId && newStatusId) {
                    fetch(`/tasks/${taskId}/toggle-status`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: 'status_id=' + newStatusId
                    });
                }
            }
        });
    });
    */
})();