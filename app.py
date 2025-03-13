from flask import Flask, render_template, request, redirect, url_for, session
from database import (init_db, add_user, get_user, get_user_role, 
                     add_project, get_projects, update_project, delete_project,
                     add_task, get_tasks, update_task, delete_task)

app = Flask(__name__)
app.secret_key = 'supersecretkey123'  # Thay bằng key bí mật của bạn

# Khởi tạo database
init_db()

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            return "Mật khẩu không khớp!"
        if get_user(username, password):
            return "Tên đăng nhập đã được sử dụng!"
        add_user(username, password, 'member', email)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    projects = get_projects()
    return render_template('dashboard.html', projects=projects)

@app.route('/add_project', methods=['POST'])
def add_project_route():
    if 'username' not in session:
        return redirect(url_for('login'))
    if get_user_role(session['username']) != 'admin':
        return "Bạn không có quyền thêm dự án!"
    name = request.form['name']
    add_project(name, session['username'])
    return redirect(url_for('dashboard'))

@app.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    if get_user_role(session['username']) != 'admin':
        return "Bạn không có quyền sửa dự án!"
    if request.method == 'POST':
        name = request.form['name']
        update_project(project_id, name)
        return redirect(url_for('dashboard'))
    projects = get_projects()
    project = next((p for p in projects if p[0] == project_id), None)
    return render_template('edit_project.html', project=project)

@app.route('/delete_project/<int:project_id>')
def delete_project_route(project_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    if get_user_role(session['username']) != 'admin':
        return "Bạn không có quyền xóa dự án!"
    delete_project(project_id)
    return redirect(url_for('dashboard'))

@app.route('/project/<int:project_id>')
def project_tasks(project_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    tasks = get_tasks(project_id)
    projects = get_projects()
    project = next((p for p in projects if p[0] == project_id), None)
    return render_template('project_tasks.html', project=project, tasks=tasks)

@app.route('/add_task/<int:project_id>', methods=['POST'])
def add_task_route(project_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    if get_user_role(session['username']) != 'admin':
        return "Bạn không có quyền thêm công việc!"
    title = request.form['title']
    assignee = request.form['assignee']
    due_date = request.form['due_date']
    add_task(title, assignee, due_date, project_id, session['username'])
    return redirect(url_for('project_tasks', project_id=project_id))

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    if get_user_role(session['username']) != 'admin':
        return "Bạn không có quyền sửa công việc!"
    if request.method == 'POST':
        title = request.form['title']
        assignee = request.form['assignee']
        due_date = request.form['due_date']
        status = request.form['status']
        update_task(task_id, title, assignee, due_date, status)
        project_id = request.form['project_id']
        return redirect(url_for('project_tasks', project_id=project_id))
    tasks = get_tasks(None)  # Lấy tất cả task để tìm task_id
    task = next((t for t in tasks if t[0] == task_id), None)
    return render_template('edit_task.html', task=task)

@app.route('/delete_task/<int:task_id>/<int:project_id>')
def delete_task_route(task_id, project_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    if get_user_role(session['username']) != 'admin':
        return "Bạn không có quyền xóa công việc!"
    delete_task(task_id)
    return redirect(url_for('project_tasks', project_id=project_id))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)