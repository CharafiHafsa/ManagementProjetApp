    document.addEventListener('DOMContentLoaded', function() {
    // CSRF token setup for AJAX
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Mark single notification as read
    document.querySelectorAll('.mark-as-read').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const notifId = this.getAttribute('data-id');
            markAsRead(notifId);
        });
    });
    
    // Delete single notification
    document.querySelectorAll('.delete-notification').forEach(button => {
        button.addEventListener('click', function() {
            const notifId = this.getAttribute('data-id');
            deleteNotification(notifId);
        });
    });
    
    // Mark all as read
    document.getElementById('mark-all-read')?.addEventListener('click', function() {
        markAllAsRead();
    });
    
    function markAsRead(notifId) {
        fetch(`/prof/notification/read/${notifId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.ok) {
                const notification = document.querySelector(`.notification-item[data-id="${notifId}"]`);
                notification.classList.remove('bg-light');
                // Optionally show a success message
            }
        })
        .catch(error => console.error('Error:', error));
    }
    
    function deleteNotification(notifId) {
        if (!confirm('Êtes-vous sûr de vouloir supprimer cette notification?')) return;
        
        fetch(`/prof/notification/delete/${notifId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.ok) {
                document.querySelector(`.notification-item[data-id="${notifId}"]`).remove();
                // Optionally show a success message
                if (document.querySelectorAll('.notification-item').length === 0) {
                    document.getElementById('notifications-container').innerHTML = 
                        '<p class="text-muted">Aucune notification pour le moment.</p>';
                    document.getElementById('mark-all-read')?.remove();
                }
            }
        })
        .catch(error => console.error('Error:', error));
    }
    
    function markAllAsRead() {
        fetch('/prof/notification/mark_all_read/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.ok) {
                document.querySelectorAll('.notification-item').forEach(item => {
                    item.classList.remove('bg-light');
                });
                document.getElementById('mark-all-read')?.remove();
                // Optionally show a success message
            }
        })
        .catch(error => console.error('Error:', error));
    }
});