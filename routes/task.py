from flask import Blueprint, jsonify, request, session, redirect, url_for
from functools import wraps
import sqlite3

task_bp = Blueprint('task', __name__)

def get_db():
    conn = sqlite3.connect('project_management.db')
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def check_role(user_id, project_id, required_role):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT Role FROM ProjectMembers WHERE UserID = ? AND ProjectID = ?", (user_id, project_id))
    role = c.fetchone()
    conn.close()
    return role and role['Role'] in required_role

@task_bp.route('/update_task_status', methods=['POST'])
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
    if not task or not check_role(current_user_id, task['ProjectID'], ['Owner', 'Leader']):
        conn.close()
        return jsonify({'success': False, 'error': 'Permission denied'}), 403

    c.execute("UPDATE Tasks SET Status = ? WHERE TaskID = ?", (status, task_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@task_bp.route('/update_task_priority', methods=['POST'])
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

@task_bp.route('/update_member_task', methods=['POST'])
@login_required
def update_member_task():
    current_user_id = session['user_id']
    data = request.get_json()
    member_id = data['member_id']
    task_id = data['task_id']  # Có thể là "" nếu bỏ gán task
    
    conn = get_db()
    c = conn.cursor()
    # Lấy ProjectID từ member
    c.execute("SELECT ProjectID, UserID FROM ProjectMembers WHERE MemberID = ?", (member_id,))
    member = c.fetchone()
    if not member or not check_role(current_user_id, member['ProjectID'], ['Owner', 'Leader']):
        conn.close()
        return jsonify({'success': False, 'error': 'Permission denied'}), 403
    
    # Nếu task_id không rỗng, kiểm tra xem task đã được gán cho user khác chưa
    if task_id:
        c.execute("SELECT AssigneeID FROM Tasks WHERE TaskID = ? AND ProjectID = ?", (task_id, member['ProjectID']))
        task = c.fetchone()
        if task and task['AssigneeID'] and task['AssigneeID'] != member['UserID']:
            conn.close()
            return jsonify({'success': False, 'error': 'Task này đã được gán cho user khác'}), 403
        
        # Gán task cho user
        c.execute("UPDATE Tasks SET AssigneeID = ? WHERE TaskID = ? AND ProjectID = ?", 
                  (member['UserID'], task_id, member['ProjectID']))
    else:
        # Bỏ gán task
        c.execute("UPDATE Tasks SET AssigneeID = NULL WHERE AssigneeID = ? AND ProjectID = ?", 
                  (member['UserID'], member['ProjectID']))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True})