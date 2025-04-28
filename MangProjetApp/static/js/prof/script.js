document.addEventListener("DOMContentLoaded", function () {
    // Alert Fade-out Logic
    let alerts = document.querySelectorAll(".fade-message");
    alerts.forEach(function(alert) {
        setTimeout(function () {
            alert.style.transition = "opacity 0.5s";
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 500); // Remove from DOM after fade-out
        }, 3000);
    });

    // Initialize Tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Modal Logic
    var modal = document.getElementById("myModal");
    var overlay = document.getElementById("modal-overlay");
    var pageWrapper = document.querySelector(".page-wrapper");

    function openModal() {
        modal.style.display = "block";
        overlay.style.display = "block";  // Show the overlay
        pageWrapper.classList.add("blurred");  // Apply blur to the page
    }

    function closeModal() {
        modal.style.display = "none";
        overlay.style.display = "none";  // Hide the overlay
        pageWrapper.classList.remove("blurred");  // Remove blur from the page
    }

    document.getElementById("openModalBtn").addEventListener("click", openModal);
    document.getElementById("closeModalBtn").addEventListener("click", closeModal);

    // Theme Toggle Logic
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme) {
        document.body.setAttribute('data-bs-theme', currentTheme);
    } else {
        document.body.setAttribute('data-bs-theme', 'light'); // Default theme
    }

    document.getElementById('themeToggle').addEventListener('click', function() {
        const currentTheme = localStorage.getItem('theme');
        if (currentTheme === 'light') {
            document.body.setAttribute('data-bs-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.setAttribute('data-bs-theme', 'light');
            localStorage.setItem('theme', 'light');
        }
    });

    // Content Change Logic
    function changeContent(view, button) {
        let views = [
            'default-view', 'instruction-view', 'announce-view', 
            'ressources-view', 'groupes-view', 'edite-view', 'supprimer-view'
        ];

        // Hide all sections
        views.forEach(function(viewId) {
            document.getElementById(viewId).style.display = 'none';
        });

        // Show the selected view
        let selectedView = document.getElementById(view + '-view');
        if (selectedView) {
            selectedView.style.display = 'block';
        } else {
            document.getElementById('default-view').style.display = 'block'; // Default view
        }

        // Remove 'selected1' class from all buttons
        let buttons = document.querySelectorAll('.btn-dashboard');
        buttons.forEach(function(btn) {
            btn.classList.remove('selected1');
        });

        // Add 'selected1' class to the clicked button
        button.classList.add('selected1');
    }

    // Set "Projets" as default on page load
    document.getElementById("default-btn").click();
});
// Function to toggle between dark and light mode
function toggleTheme() {
    const currentTheme = localStorage.getItem('theme');
    const themeToggleIcon = document.querySelector('#themeToggle .iconify');
    const themeToggleButton = document.getElementById('themeToggle');
    let tooltip = bootstrap.Tooltip.getInstance(themeToggleButton); // Check if tooltip is already initialized
  
    // If tooltip is initialized, destroy it before re-initializing
    if (tooltip) {
      tooltip.dispose();
    }
  
    // If the current theme is light, switch to dark
    if (currentTheme === 'light') {
      document.body.setAttribute('data-bs-theme', 'dark');
      localStorage.setItem('theme', 'dark');
      // Change the icon to a moon icon for dark mode
      themeToggleIcon.setAttribute('data-icon', 'solar:moon-outline');
      // Change the tooltip to dark mode
      themeToggleButton.setAttribute('title', 'dark');
    } else {
      document.body.setAttribute('data-bs-theme', 'light');
      localStorage.setItem('theme', 'light');
      // Change the icon to a sun icon for light mode
      themeToggleIcon.setAttribute('data-icon', 'solar:sun-outline');
      // Change the tooltip to light mode
      themeToggleButton.setAttribute('title', 'light');
    }
  
    // Re-initialize the tooltip with the new title
    new bootstrap.Tooltip(themeToggleButton);
  }
  
  // Check localStorage for the saved theme on page load
  window.addEventListener('load', function() {
    const savedTheme = localStorage.getItem('theme');
    const themeToggleIcon = document.querySelector('#themeToggle .iconify');
    const themeToggleButton = document.getElementById('themeToggle');
    
    let tooltip = bootstrap.Tooltip.getInstance(themeToggleButton); // Check if tooltip is already initialized
  
    // If tooltip is initialized, destroy it before re-initializing
    if (tooltip) {
      tooltip.dispose();
    }
  
    if (savedTheme) {
      document.body.setAttribute('data-bs-theme', savedTheme);
      // Set the appropriate icon based on the saved theme
      if (savedTheme === 'dark') {
        themeToggleIcon.setAttribute('data-icon', 'solar:moon-outline');
        themeToggleButton.setAttribute('title', 'dark');
      } else {
        themeToggleIcon.setAttribute('data-icon', 'solar:sun-outline');
        themeToggleButton.setAttribute('title', 'light');
      }
    } else {
      // Default theme (light) if no saved theme exists
      document.body.setAttribute('data-bs-theme', 'light');
      themeToggleIcon.setAttribute('data-icon', 'solar:sun-outline');
      themeToggleButton.setAttribute('title', 'light');
    }
  
    // Re-initialize the tooltip with the new title
    new bootstrap.Tooltip(themeToggleButton);
  });
  
  // Attach the event listener to the theme toggle button
  document.getElementById('themeToggle').addEventListener('click', toggleTheme);
  

  function toggleSearchInput() {
    var searchInput = document.getElementById("searchInput");
    // Toggle visibility of the search input
    if (searchInput.style.display === "none" || searchInput.style.display === "") {
        searchInput.style.display = "inline-block"; // Show input
    } else {
        searchInput.style.display = "none"; // Hide input
    }
}

document.addEventListener("DOMContentLoaded", function () {
  const counters = document.querySelectorAll(".count");
  counters.forEach(counter => {
      let target = +counter.getAttribute("data-target");
      let count = 0;
      let increment = target > 0 ? target / 50 : 1; // Ensure increment is at least 1

      function updateCount() {
          if (count < target) {
              count += increment;
              counter.innerText = Math.ceil(count);
              setTimeout(updateCount, 20);  // You can increase this value if the count is too fast
          } else {
              counter.innerText = target;
          }
      }
      updateCount();
  });
});

