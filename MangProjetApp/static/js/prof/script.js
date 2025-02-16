let btn = document.querySelector('#btn');
let sidebar = document.querySelector('.sidebar');
let searchBtn = document.querySelector('.bx-search');
let links = document.querySelectorAll('.nav_list a');

// Toggle Sidebar
btn.onclick = function () {
    sidebar.classList.toggle("active");
};
searchBtn.onclick = function () {
    sidebar.classList.toggle("active");
};

// Handle Dynamic Page Loading
links.forEach(link => {
    link.addEventListener('click', function (e) {
        e.preventDefault(); // Prevent default anchor behavior
        const page = this.getAttribute('data-page'); // Get the target page

        if (page) {
            fetch(page) // Load the page using fetch
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Page not found');
                    }
                    return response.text();
                })
                .then(data => {
                    document.getElementById('content').innerHTML = data; // Update the content
                })
                .catch(error => {
                    document.getElementById('content').innerHTML = `<p>Error loading page: ${error.message}</p>`;
                });
        }
    });
});



