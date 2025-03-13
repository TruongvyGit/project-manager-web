document.addEventListener('DOMContentLoaded', function() {
    // Nhắc nhở công việc
    const today = new Date().toISOString().split('T')[0];
    document.querySelectorAll('input[type="date"]').forEach(input => {
        input.addEventListener('change', function() {
            if (this.value === today) {
                alert('Công việc này cần hoàn thành hôm nay!');
            }
        });
    });
});

// Hàm bật/tắt hiển thị mật khẩu
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const button = input.nextElementSibling;
    if (input.type === 'password') {
        input.type = 'text';
        button.textContent = 'Ẩn';
    } else {
        input.type = 'password';
        button.textContent = 'Hiện';
    }
}