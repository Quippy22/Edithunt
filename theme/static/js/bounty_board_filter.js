document.addEventListener('DOMContentLoaded', function() {
    // --- Filter Form Reset Logic ---
    const form = document.getElementById('filter-form');
    const resetBtn = document.getElementById('reset-filters');

    if (resetBtn && form) {
        resetBtn.addEventListener('click', function() {
            const inputs = form.querySelectorAll('input, select');
            inputs.forEach(input => {
                if (input.type === 'text' || input.type === 'number') {
                    input.value = '';
                } else if (input.tagName === 'SELECT') {
                     if (input.multiple) {
                        Array.from(input.options).forEach(option => option.selected = false);
                    } else {
                         input.selectedIndex = 0;
                    }
                }
            });
            form.submit();
        });
    }

    // --- Back to Top Button Logic ---
    const backToTopBtn = document.getElementById('back-to-top');
    
    if (backToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTopBtn.classList.remove('opacity-0', 'pointer-events-none');
                backToTopBtn.classList.add('opacity-100', 'pointer-events-auto');
            } else {
                backToTopBtn.classList.remove('opacity-100', 'pointer-events-auto');
                backToTopBtn.classList.add('opacity-0', 'pointer-events-none');
            }
        });

        backToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
});
