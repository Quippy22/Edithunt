document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('filter-form');
    if (form) {
        // Use event delegation to listen for changes on form inputs
        form.addEventListener('change', function(event) {
            // We can add checks here if we want to exclude certain inputs
            // from triggering an auto-submit, but for now, any change will submit.
            form.submit();
        });
    }
});
