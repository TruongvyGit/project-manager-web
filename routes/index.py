from flask import Blueprint, render_template, redirect, url_for, session, flash
from functools import wraps
import sqlite3

index_bp = Blueprint('index', __name__)

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

@index_bp.route('/')
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

@index_bp.route('/project/<int:project_id>')
@login_required
def project(project_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM Projects WHERE ProjectID = ?", (project_id,))
    project = c.fetchone()
    if not project:
        conn.close()
        flash("Project không tồn tại hoặc đã bị xóa")
        return redirect(url_for('index.index'))  # Sửa từ 'index' thành 'index.index'
    c.execute("SELECT Role FROM ProjectMembers WHERE UserID = ? AND ProjectID = ?", (session['user_id'], project_id))
    member = c.fetchone()
    if not member:
        conn.close()
        flash("Bạn không có quyền truy cập project này")
        return redirect(url_for('index.index'))  # Sửa từ 'index' thành 'index.index'
    c.execute("""
        SELECT pm.*, u.Name, u.Email 
        FROM ProjectMembers pm 
        JOIN Users u ON pm.UserID = u.UserID 
        WHERE pm.ProjectID = ?
    """, (project_id,))
    members = c.fetchall()
    c.execute("""
        SELECT t.*, u.Name AS AssigneeName 
        FROM Tasks t 
        LEFT JOIN Users u ON t.AssigneeID = u.UserID 
        WHERE t.ProjectID = ?
    """, (project_id,))
    tasks = c.fetchall()
    conn.close()
    return render_template('project.html', project=project, members=members, tasks=tasks)