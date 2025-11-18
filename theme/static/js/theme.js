const themeToggle = document.getElementById('theme-toggle');

// Set initial state of the toggle
if (document.documentElement.classList.contains('dark')) {
    if (themeToggle) themeToggle.checked = true;
}

// Toggle theme on checkbox change
if (themeToggle) {
    themeToggle.addEventListener('change', function() {
        if (this.checked) {
            document.documentElement.classList.add('dark');
            localStorage.setItem('color-theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('color-theme', 'light');
        }
    });
}
