// Initialize theme switch
const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
const currentTheme = localStorage.getItem('theme');

// Set initial theme if it exists in localStorage
if (currentTheme) {
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    // Set checkbox state if it exists
    if (toggleSwitch && currentTheme === 'dark') {
        toggleSwitch.checked = true;
    }
}

// Theme switching function
function switchTheme(e) {
    if (e.target.checked) {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
    }
}

// Add event listener only if toggleSwitch exists
if (toggleSwitch) {
    toggleSwitch.addEventListener('change', switchTheme, false);
} else {
    console.log('Theme switch not found in the DOM');
}

// Add event listener for DOMContentLoaded to ensure elements exist
document.addEventListener('DOMContentLoaded', function() {
    const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
    if (toggleSwitch) {
        toggleSwitch.addEventListener('change', switchTheme, false);
    }
});