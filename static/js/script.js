function openPopup(url) {
    fetch(url)
        .then(response => response.text())
        .then(html => {
            document.getElementById('popupContainer').innerHTML = html;
            const modal = new bootstrap.Modal(document.getElementById('actionModal'));
            modal.show();

            document.getElementById('popupForm').addEventListener('submit', function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                fetch(url, {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    modal.hide();
                    if (url.includes('delete_project')) {
                        window.location.href = '/';
                    } else {
                        window.location.reload();
                    }
                })
                .catch(error => {
                    alert('An error occurred: ' + error);
                });
            });
        });
}