$(document).ready(function() {
    // Function to apply filters via AJAX
    function applyFilters() {
        const formData = $('#filter-form').serialize();

        $.ajax({
            url: '/workout/library/',
            type: 'GET',
            data: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(data) {
                // Update the exercises grid with new content
                $('.exercises-grid').html(data.exercises_html);
            },
            error: function(xhr) {
                console.error('Failed to apply filters:', xhr);
            }
        });
    }

    // Auto-apply filter when dropdown changes
    $('.filter-select').on('change', function() {
        applyFilters();
    });

    // Debounced text input for name filter
    let nameInputTimeout;
    $('.filter-input').on('input', function() {
        clearTimeout(nameInputTimeout);
        nameInputTimeout = setTimeout(function() {
            applyFilters();
        }, 500); // Wait 500ms after user stops typing
    });

    // Prevent form submission (we handle it via AJAX)
    $('#filter-form').on('submit', function(e) {
        e.preventDefault();
        applyFilters();
    });

    // Reset filters button
    $('#reset-filters').on('click', function() {
        // Clear all form inputs
        $('#name').val('');
        $('#muscle_group').val('');
        $('#difficulty').val('');
        $('#equipment').val('');

        // Apply filters (which will now show all exercises)
        applyFilters();
    });

    // Optional: Add smooth scroll for long pages
    $('html').css('scroll-behavior', 'smooth');

    // Export data button
    $('#export-btn').on('click', function() {
        const $btn = $(this);
        const originalText = $btn.text();
        $btn.prop('disabled', true).text('Exporting...');

        window.location.href = '/workout/export_data/';

        // Re-enable button after a short delay
        setTimeout(function() {
            $btn.prop('disabled', false).text(originalText);
        }, 2000);
    });

    // Import data button - opens file picker
    $('#import-btn').on('click', function() {
        $('#import-file').click();
    });

    // Clear data button
    $('#clear-btn').on('click', function() {
        const confirmMsg = 'WARNING: This will DELETE all workout data including exercises, workouts, logs, and settings. This action cannot be undone!\n\nAre you absolutely sure?';

        if (!confirm(confirmMsg)) {
            return;
        }

        const $btn = $(this);
        const originalText = $btn.text();
        $btn.prop('disabled', true).text('Clearing...');
        showMessage('Clearing all data...', 'info');

        // Get CSRF token
        const csrfToken = getCookie('csrftoken');

        $.ajax({
            url: '/workout/clear_data/',
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            success: function(response) {
                showMessage('All data cleared successfully! Reloading page...', 'success');
                // Reload page to show updated data
                setTimeout(function() {
                    location.reload();
                }, 1500);
            },
            error: function(xhr) {
                let errorMsg = 'Failed to clear data';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg += ': ' + xhr.responseJSON.error;
                }
                showMessage(errorMsg, 'error');
                $btn.prop('disabled', false).text(originalText);
            }
        });
    });

    // Handle file selection for import
    $('#import-file').on('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;

        // Check file type
        if (!file.name.endsWith('.json')) {
            showMessage('Please select a JSON file', 'error');
            $(this).val('');
            return;
        }

        // Ask user to confirm
        const confirmMsg = 'Are you sure you want to import this data? This will update existing records and add new ones.';

        if (!confirm(confirmMsg)) {
            $(this).val('');
            return;
        }

        // Create FormData and upload
        const formData = new FormData();
        formData.append('file', file);

        // Get CSRF token
        const csrfToken = getCookie('csrftoken');

        // Show loading state
        const $importBtn = $('#import-btn');
        const originalText = $importBtn.text();
        $importBtn.prop('disabled', true).text('Importing...');
        showMessage('Importing data...', 'info');

        $.ajax({
            url: '/workout/import_data/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': csrfToken
            },
            success: function(response) {
                showMessage('Data imported successfully! Reloading page...', 'success');
                // Reload page to show updated data
                setTimeout(function() {
                    location.reload();
                }, 1500);
            },
            error: function(xhr) {
                let errorMsg = 'Failed to import data';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg += ': ' + xhr.responseJSON.error;
                }
                showMessage(errorMsg, 'error');
            },
            complete: function() {
                // Reset button state
                $importBtn.prop('disabled', false).text(originalText);
                // Reset file input
                $('#import-file').val('');
            }
        });
    });

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Helper function to show messages
    function showMessage(message, type) {
        const $messageArea = $('#message-area');
        const className = type === 'error' ? 'error-message' :
                         type === 'success' ? 'success-message' : 'info-message';
        $messageArea.html(`<div class="${className}">${message}</div>`);

        // Clear message after 5 seconds for success/info
        if (type !== 'error') {
            setTimeout(function() {
                $messageArea.html('');
            }, 5000);
        }
    }
});
