from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from modules.edit_project import edit_project_bp
from modules.edit_task import edit_task_bp
from modules.edit_member import edit_member_bp
from database import init_db
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Thay bằng key bí mật của bạn

# Đăng ký các Blueprint
app.register_blueprint(edit_project_bp)
app.register_blueprint(edit_task_bp)
app.register_blueprint(edit_member_bp)

# Khởi tạo DB
init_db()

def get_db():
    conn = sqlite3.connect('project_management.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM Projects WHERE CreatorID = ?", (session['user_id'],))
    created_projects = c.fetchall()
    c.execute("""
        SELECT p.*, pm.Role 
        FROM Projects p 
        JOIN ProjectMembers pm ON p.ProjectID = pm.ProjectID 
        WHERE pm.UserID = ? AND pm.Role != 'Owner'
    """, (session['user_id'],))
    participated_projects = c.fetchall()
    conn.close()
    return render_template('index.html', created_projects=created_projects, participated_projects=participated_projects)

@app.route('/project/<int:project_id>')
@login_required
def project(project_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM Projects WHERE ProjectID = ?", (project_id,))
    project = c.fetchone()
    if not project:
        conn.close()
        flash("Project không tồn tại hoặc đã bị xóa")
        return redirect(url_for('index'))
    c.execute("SELECT Role FROM ProjectMembers WHERE UserID = ? AND ProjectID = ?", (session['user_id'], project_id))
    member = c.fetchone()
    if not member:
        conn.close()
        flash("Bạn không có quyền truy cập project này")
        return redirect(url_for('index'))
    user_role = member['Role']
    
    # Lấy danh sách members kèm số lượng task được giao
    c.execute("""
        SELECT pm.*, u.Name, u.Email, 
               (SELECT COUNT(*) FROM Tasks t WHERE t.AssigneeID = pm.UserID AND t.ProjectID = pm.ProjectID) AS TaskCount
        FROM ProjectMembers pm 
        JOIN Users u ON pm.UserID = u.UserID 
        WHERE pm.ProjectID = ?
    """, (project_id,))
    members = c.fetchall()

    if user_role == 'Member':
        c.execute("""
            SELECT t.*, u.Name AS AssigneeName 
            FROM Tasks t 
            LEFT JOIN Users u ON t.AssigneeID = u.UserID 
            WHERE t.ProjectID = ? AND t.AssigneeID = ?
        """, (project_id, session['user_id']))
    else:
        c.execute("""
            SELECT t.*, u.Name AS AssigneeName 
            FROM Tasks t 
            LEFT JOIN Users u ON t.AssigneeID = u.UserID 
            WHERE t.ProjectID = ?
        """, (project_id,))
    tasks = c.fetchall()
    conn.close()
    return render_template('project.html', project=project, members=members, tasks=tasks, user_role=user_role)

@app.route('/task/<int:task_id>')
@login_required
def task_detail(task_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT t.*, p.ProjectName, u.Name AS AssigneeName 
        FROM Tasks t 
        JOIN Projects p ON t.ProjectID = p.ProjectID 
        LEFT JOIN Users u ON t.AssigneeID = u.UserID 
        WHERE t.TaskID = ?
    """, (task_id,))
    task = c.fetchone()
    if not task:
        conn.close()
        flash("Task không tồn tại")
        return redirect(url_for('index'))
    c.execute("SELECT Role FROM ProjectMembers WHERE UserID = ? AND ProjectID = ?", (session['user_id'], task['ProjectID']))
    member = c.fetchone()
    if not member or (member['Role'] == 'Member' and task['AssigneeID'] != session['user_id']):
        conn.close()
        flash("Bạn không có quyền xem chi tiết task này")
        return redirect(url_for('index'))
    conn.close()
    return render_template('task_detail.html', task=task)

@app.route('/member/<int:member_id>')
@login_required
def member_detail(member_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT pm.*, u.Name, u.Email, p.ProjectID, p.ProjectName
        FROM ProjectMembers pm 
        JOIN Users u ON pm.UserID = u.UserID 
        JOIN Projects p ON pm.ProjectID = p.ProjectID 
        WHERE pm.MemberID = ?
    """, (member_id,))
    member = c.fetchone()
    if not member:
        conn.close()
        flash("Member không tồn tại")
        return redirect(url_for('index'))
    
    # Kiểm tra quyền: Chỉ Owner/Leader được xem chi tiết
    if not check_role(session['user_id'], member['ProjectID'], ['Owner', 'Leader']):
        conn.close()
        flash("Bạn không có quyền xem chi tiết member này")
        return redirect(url_for('index'))
    
    # Lấy danh sách tasks của member trong project
    c.execute("""
        SELECT t.* 
        FROM Tasks t 
        WHERE t.ProjectID = ? AND t.AssigneeID = ?
    """, (member['ProjectID'], member['UserID']))
    tasks = c.fetchall()
    conn.close()
    return render_template('member_detail.html', member=member, tasks=tasks)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_id = request.form['login_id']
        password = request.form['password']
        
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM Users WHERE Username = ? OR Email = ?", (login_id, login_id))
        user = c.fetchone()
        conn.close()
        
        if not user:
            flash("Username hoặc Email không tồn tại")
            return redirect(url_for('login'))
        if user['Password'] != password:
            flash("Mật khẩu không đúng")
            return redirect(url_for('login'))
        
        session['user_id'] = user['UserID']
        session['username'] = user['Username']
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM Users WHERE Username = ?", (username,))
        if c.fetchone():
            flash("Username đã tồn tại")
            return redirect(url_for('register'))
        c.execute("SELECT * FROM Users WHERE Email = ?", (email,))
        if c.fetchone():
            flash("Email đã tồn tại")
            return redirect(url_for('register'))
        if password != confirm_password:
            flash("Mật khẩu không khớp")
            return redirect(url_for('register'))
        
        c.execute("INSERT INTO Users (Username, Name, Email, Password) VALUES (?, ?, ?, ?)", 
                  (username, name, email, password))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        
        session['user_id'] = user_id
        session['username'] = username
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/update_task_status', methods=['POST'])
@login_required
def update_task_status():
    current_user_id = session['user_id']
    data = request.get_json()
    task_id = data['task_id']
    status = data['status']
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT ProjectID FROM Tasks WHERE TaskID = ?", (task_id,))
    task = c.fetchone()
    if not task:
        conn.close()
        return jsonify({'success': False, 'error': 'Task not found'}), 404

    if not check_role(current_user_id, task['ProjectID'], ['Owner', 'Leader', 'Member']):
        conn.close()
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    c.execute("UPDATE Tasks SET Status = ? WHERE TaskID = ?", (status, task_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/update_task_priority', methods=['POST'])
@login_required
def update_task_priority():
    current_user_id = session['user_id']
    data = request.get_json()
    task_id = data['task_id']
    priority = data['priority']
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT ProjectID FROM Tasks WHERE TaskID = ?", (task_id,))
    task = c.fetchone()
    if not task or not check_role(current_user_id, task['ProjectID'], ['Owner', 'Leader']):
        conn.close()
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    c.execute("UPDATE Tasks SET Priority = ? WHERE TaskID = ?", (priority, task_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/update_task_assignee', methods=['POST'])
@login_required
def update_task_assignee():
    current_user_id = session['user_id']
    data = request.get_json()
    task_id = data['task_id']
    assignee_id = data['assignee_id'] if data['assignee_id'] else None
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT ProjectID FROM Tasks WHERE TaskID = ?", (task_id,))
    task = c.fetchone()
    if not task or not check_role(current_user_id, task['ProjectID'], ['Owner', 'Leader']):
        conn.close()
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    if assignee_id:
        c.execute("SELECT UserID FROM ProjectMembers WHERE UserID = ? AND ProjectID = ?", (assignee_id, task['ProjectID']))
        valid_assignee = c.fetchone()
        if not valid_assignee:
            conn.close()
            return jsonify({'success': False, 'error': 'Assignee must be a member of this project'}), 403

    c.execute("UPDATE Tasks SET AssigneeID = ? WHERE TaskID = ?", (assignee_id, task_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

def check_role(user_id, project_id, required_role):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT Role FROM ProjectMembers WHERE UserID = ? AND ProjectID = ?", (user_id, project_id))
    role = c.fetchone()
    conn.close()
    return role and role['Role'] in required_role

if __name__ == '__main__':
    app.run(debug=True)