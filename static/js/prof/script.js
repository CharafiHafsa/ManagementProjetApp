function changeContent(view, button) {
    // Hide all sections
    document.getElementById('default-view').style.display = 'none';
    document.getElementById('instruction-view').style.display = 'none';
    document.getElementById('announce-view').style.display = 'none';
    document.getElementById('ressources-view').style.display = 'none';
    document.getElementById('groupes-view').style.display = 'none';
    document.getElementById('edite-view').style.display = 'none';
    document.getElementById('supprimer-view').style.display = 'none';

    // Show selected view
    if (view === 'instruction') {
        document.getElementById('instruction-view').style.display = 'block';
    } else if (view === 'announce') {
        document.getElementById('announce-view').style.display = 'block';
    } else if (view === 'ressource') {
        document.getElementById('ressources-view').style.display = 'block';
    } else if (view === 'groupes') {
        document.getElementById('groupes-view').style.display = 'block';
    } else if (view === 'edite') {
        document.getElementById('edite-view').style.display = 'block';
    } else if (view === 'supprimer') {
        document.getElementById('supprimer-view').style.display = 'block';
    } else {
        document.getElementById('default-view').style.display = 'block';
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
window.onload = function() {
    document.getElementById("default-btn").click();
};


