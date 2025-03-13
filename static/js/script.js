document.addEventListener('DOMContentLoaded', function() {
    const today = new Date().toISOString().split('T')[0];
    document.querySelectorAll('input[type="date"]').forEach(input => {
        input.addEventListener('change', function() {
            if (this.value === today) {
                alert('Công việc này cần hoàn thành hôm nay!');
            }
        });
    });
});