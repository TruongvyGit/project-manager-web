from flask import Flask, render_template, request, redirect, url_for, session
from database import init_db, add_user, get_user, add_task, get_tasks, get_user_role

app = Flask(__name__)
app.secret_key = 'supersecretkey123'  # Thay bằng key bí mật của bạn

# Khởi tạo database khi ứng dụng chạy
init_db()

# Trang chủ
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

# Đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username, password)
        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        return "Sai thông tin đăng nhập!"
    return render_template('login.html')

# Đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Kiểm tra mật khẩu khớp
        if password != confirm_password:
            return "Mật khẩu không khớp!"
        
        # Kiểm tra username đã tồn tại chưa
        if get_user(username, password):  # Chỉ kiểm tra username tồn tại
            return "Tên đăng nhập đã được sử dụng!"
        
        # Thêm người dùng mới
        add_user(username, password, 'member')  # Mặc định role là member
        return redirect(url_for('login'))
    return render_template('register.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    tasks = get_tasks()
    return render_template('dashboard.html', tasks=tasks)

# Thêm công việc
@app.route('/add_task', methods=['POST'])
def add_task_route():
    if 'username' not in session:
        return redirect(url_for('login'))
    if get_user_role(session['username']) != 'admin':
        return "Bạn không có quyền thêm công việc!"
    title = request.form['title']
    assignee = request.form['assignee']
    due_date = request.form['due_date']
    add_task(title, assignee, due_date, session['username'])
    return redirect(url_for('dashboard'))

# Đăng xuất
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)