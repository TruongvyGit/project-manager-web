from flask import Flask, render_template, request, redirect, url_for, session
from database import (init_db, add_user, get_user, get_user_by_username, get_all_users, get_user_role, get_project_role, 
                     add_project, add_project_member, get_projects, get_project_member_count, get_project_task_count, 
                     update_project, delete_project, add_label, get_labels, update_label, delete_label, add_task, 
                     get_tasks, update_task, delete_task, request_join_project, get_pending_requests, approve_member, 
                     remove_member, update_member_role, get_project_members, get_my_projects, get_joined_projects)

app = Flask(__name__)
app.secret_key = 'supersecretkey123'

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
        add_user(username, password, 'user', email)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    my_projects = get_my_projects(session['username'])
    joined_projects = get_joined_projects(session['username'])
    all_projects = get_projects()
    role = get_user_role(session['username'])
    all_users = get_all_users()

    # Lấy số thành viên và nhiệm vụ cho từng dự án
    my_projects_with_details = [
        (project, get_project_member_count(project[0]), get_project_task_count(project[0]))
        for project in my_projects
    ]
    joined_projects_with_details = [
        (project, get_project_member_count(project[0]), get_project_task_count(project[0]))
        for project in joined_projects
    ]

    return render_template('dashboard.html', my_projects=my_projects_with_details, 
                          joined_projects=joined_projects_with_details, all_projects=all_projects, 
                          role=role, all_users=all_users)

@app.route('/add_project', methods=['POST'])
def add_project_route():
    if 'username' not in session:
        return redirect(url_for('login'))
    name = request.form['name']
    project_id = add_project(name, session['username'])
    
    # Thêm thành viên nếu có
    members = request.form.getlist('members')
    roles = request.form.getlist('roles')
    for member, role in zip(members, roles):
        if member and role:
            add_project_member(project_id, member, role)
    
    return redirect(url_for('dashboard'))

@app.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    user_role = get_user_role(session['username'])
    project_role = get_project_role(project_id, session['username'])
    if user_role != 'admin' and project_role != 'Leader':
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
    user_role = get_user_role(session['username'])
    project_role = get_project_role(project_id, session['username'])
    if user_role != 'admin' and project_role != 'Leader':
        return "Bạn không có quyền xóa dự án!"
    delete_project(project_id)
    return redirect(url_for('dashboard'))

@app.route('/project/<int:project_id>')
def project_tasks(project_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    project_role = get_project_role(project_id, session['username'])
    user_role = get_user_role(session['username'])
    if not project_role and user_role != 'admin':
        return "Bạn không có quyền truy cập dự án này!"
    tasks = get_tasks(project_id)
    projects = get_projects()
    labels = get_labels()
    project = next((p for p in projects if p[0] == project_id), None)
    members = get_project_members(project_id)
    pending_requests = get_pending_requests(project_id)
    return render_template('project_tasks.html', project=project, tasks=tasks, labels=labels, project_role=project_role, 
                          members=members, pending_requests=pending_requests, user_role=user_role)

@app.route('/add_task/<int:project_id>', methods=['POST'])
def add_task_route(project_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    user_role = get_user_role(session['username'])
    project_role = get_project_role(project_id, session['username'])
    if user_role != 'admin' and project_role != 'Leader':
        return "Bạn không có quyền thêm công việc!"
    title = request.form['title']
    assignee = request.form['assignee']
    due_date = request.form['due_date']
    label_id = request.form['label_id'] if request.form['label_id'] else None
    description = request.form['description']
    add_task(title, assignee, due_date, project_id, label_id, session['username'], description)
    return redirect(url_for('project_tasks', project_id=project_id))

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    tasks = get_tasks(None)
    task = next((t for t in tasks if t[0] == task_id), None)
    if not task:
        return "Công việc không tồn tại!", 404
    user_role = get_user_role(session['username'])
    project_role = get_project_role(task[4], session['username'])
    if user_role != 'admin' and project_role != 'Leader':
        return "Bạn không có quyền sửa công việc!"
    if request.method == 'POST':
        title = request.form['title']
        assignee = request.form['assignee']
        due_date = request.form['due_date']
        label_id = request.form['label_id'] if request.form['label_id'] else None
        status = request.form['status']
        description = request.form['description']
        update_task(task_id, title, assignee, due_date, label_id, status, description)
        project_id = request.form['project_id']
        return redirect(url_for('project_tasks', project_id=project_id))
    labels = get_labels()
    return render_template('edit_task.html', task=task, labels=labels)

@app.route('/delete_task/<int:task_id>/<int:project_id>')
def delete_task_route(task_id, project_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    user_role = get_user_role(session['username'])
    project_role = get_project_role(project_id, session['username'])
    if user_role != 'admin' and project_role != 'Leader':
        return "Bạn không có quyền xóa công việc!"
    delete_task(task_id)
    return redirect(url_for('project_tasks', project_id=project_id))

@app.route('/add_label/<int:project_id>', methods=['POST'])
def add_label_route(project_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    user_role = get_user_role(session['username'])
    project_role = get_project_role(project_id, session['username'])
    if user_role != 'admin' and project_role != 'Leader':
        return "Bạn không có quyền thêm nhãn!"
    name = request.form['label_name']
    add_label(name, session['username'])
    return redirect(url_for('project_tasks', project_id=project_id))

@app.route('/edit_label/<int:label_id>/<int:project_id>', methods=['GET', 'POST'])
def edit_label(label_id, project_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    user_role = get_user_role(session['username'])
    project_role = get_project_role(project_id, session['username'])
    if user_role != 'admin' and project_role != 'Leader':
        return "Bạn không có quyền sửa nhãn!"
    if request.method == 'POST':
        name = request.form['label_name']
        update_label(label_id, name)
        return redirect(url_for('project_tasks', project_id=project_id))
    labels = get_labels()
    label = next((l for l in labels if l[0] == label_id), None)
    return render_template('edit_label.html', label=label, project_id=project_id)

@app.route('/delete_label/<int:label_id>/<int:project_id>')
def delete_label_route(label_id, project_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    user_role = get_user_role(session['username'])
    project_role = get_project_role(project_id, session['username'])
    if user_role != 'admin' and project_role != 'Leader':
        return "Bạn không có quyền xóa nhãn!"
    delete_label(label_id)
    return redirect(url_for('project_tasks', project_id=project_id))

@app.route('/update_task_status/<int:task_id>/<int:project_id>', methods=['POST'])
def update_task_status(task_id, project_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    task = next((t for t in get_tasks(project_id) if t[0] == task_id), None)
    if not task:
        return "Công việc không tồn tại!", 404
    is_checked = request.form.get('completed') == 'on'
    if is_checked:
        status = 'done'
    else:
        status = request.form.get('status', 'todo')
    update_task(task_id, task[1], task[2], task[3], task[5], status, task[8])
    return redirect(url_for('project_tasks', project_id=project_id))

@app.route('/request_join/<int:project_id>')
def request_join(project_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    request_join_project(project_id, session['username'])
    return redirect(url_for('dashboard'))

@app.route('/approve_member/<int:request_id>/<int:project_id>')
def approve_member_route(request_id, project_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    user_role = get_user_role(session['username'])
    project_role = get_project_role(project_id, session['username'])
    if user_role != 'admin' and project_role != 'Leader':
        return "Bạn không có quyền phê duyệt!"
    approve_member(request_id)
    return redirect(url_for('project_tasks', project_id=project_id))

@app.route('/remove_member/<int:project_id>/<int:user_id>')
def remove_member_route(project_id, user_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    user_role = get_user_role(session['username'])
    project_role = get_project_role(project_id, session['username'])
    if user_role != 'admin' and project_role != 'Leader':
        return "Bạn không có quyền xóa thành viên!"
    remove_member(project_id, user_id)
    return redirect(url_for('project_tasks', project_id=project_id))

@app.route('/leave_project/<int:project_id>')
def leave_project(project_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    user = get_user_by_username(session['username'])
    user_role = get_user_role(session['username'])
    project_role = get_project_role(project_id, session['username'])
    if project_role == 'Leader' and user_role != 'admin':
        return "Bạn là Leader, không thể rời dự án!"
    remove_member(project_id, user[0])
    return redirect(url_for('dashboard'))

@app.route('/assign_role/<int:project_id>/<int:user_id>', methods=['POST'])
def assign_role(project_id, user_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    user_role = get_user_role(session['username'])
    project_role = get_project_role(project_id, session['username'])
    if user_role != 'admin' and project_role != 'Leader':
        return "Bạn không có quyền thay đổi vai trò!"
    new_role = request.form['role']
    update_member_role(project_id, user_id, new_role)
    return redirect(url_for('project_tasks', project_id=project_id))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)