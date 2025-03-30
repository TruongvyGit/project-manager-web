from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
import sqlite3
from datetime import datetime

edit_task_bp = Blueprint('edit_task', __name__)

def get_db():
    conn = sqlite3.connect('project_management.db')
    conn.row_factory = sqlite3.Row
    return conn

def check_role(user_id, project_id, required_role):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT Role FROM ProjectMembers WHERE UserID = ? AND ProjectID = ?", (user_id, project_id))
    role = c.fetchone()
    conn.close()
    return role and role['Role'] in required_role

@edit_task_bp.route('/project/<int:project_id>/create_task', methods=['GET', 'POST'])
def create_task(project_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    current_user_id = session['user_id']
    if not check_role(current_user_id, project_id, ['Owner', 'Leader']):
        return jsonify({'error': 'Permission denied'}), 403
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        status = request.form['status']
        priority = request.form['priority']
        assignee_id = request.form['assignee_id']
        start_datetime = request.form['start_datetime']
        due_datetime = request.form['due_datetime']
        is_completed = request.form.get('is_completed')

        if is_completed == 'on':
            status = 'Completed'

        try:
            if start_datetime:
                datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M')
            if due_datetime:
                datetime.strptime(due_datetime, '%Y-%m-%dT%H:%M')
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD HH:MM'}), 400

        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT UserID FROM ProjectMembers WHERE UserID = ? AND ProjectID = ?", (assignee_id, project_id))
        valid_assignee = c.fetchone()
        if assignee_id and not valid_assignee:
            conn.close()
            return jsonify({'error': 'Assignee must be a member of this project'}), 403
        
        c.execute("INSERT INTO Tasks (TaskName, Description, Status, Priority, AssigneeID, CreatorID, ProjectID, StartDateTime, DueDateTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                  (name, description, status, priority, assignee_id, current_user_id, project_id, start_datetime or None, due_datetime or None))
        conn.commit()
        conn.close()
        return redirect(url_for('project', project_id=project_id))
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT u.UserID, u.Name FROM Users u JOIN ProjectMembers pm ON u.UserID = pm.UserID WHERE pm.ProjectID = ?", (project_id,))
    users = c.fetchall()
    conn.close()
    return render_template('popup.html', action='create_task', project_id=project_id, users=users)

@edit_task_bp.route('/project/<int:project_id>/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(project_id, task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    current_user_id = session['user_id']
    role_allowed = ['Owner', 'Leader'] if request.method == 'POST' else ['Owner', 'Leader', 'Member']
    if not check_role(current_user_id, project_id, role_allowed):
        return jsonify({'error': 'Permission denied'}), 403
    conn = get_db()
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form['name'] if check_role(current_user_id, project_id, ['Owner', 'Leader']) else None
        description = request.form['description'] if check_role(current_user_id, project_id, ['Owner', 'Leader']) else None
        status = request.form['status']
        priority = request.form['priority'] if check_role(current_user_id, project_id, ['Owner', 'Leader']) else None
        assignee_id = request.form['assignee_id'] if check_role(current_user_id, project_id, ['Owner', 'Leader']) else None
        start_datetime = request.form['start_datetime'] if check_role(current_user_id, project_id, ['Owner', 'Leader']) else None
        due_datetime = request.form['due_datetime'] if check_role(current_user_id, project_id, ['Owner', 'Leader']) else None
        is_completed = request.form.get('is_completed')

        if is_completed == 'on':
            status = 'Completed'

        try:
            if start_datetime:
                datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M')
            if due_datetime:
                datetime.strptime(due_datetime, '%Y-%m-%dT%H:%M')
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD HH:MM'}), 400

        if assignee_id:
            c.execute("SELECT UserID FROM ProjectMembers WHERE UserID = ? AND ProjectID = ?", (assignee_id, project_id))
            valid_assignee = c.fetchone()
            if not valid_assignee:
                conn.close()
                return jsonify({'error': 'Assignee must be a member of this project'}), 403
        
        c.execute("UPDATE Tasks SET TaskName = COALESCE(?, TaskName), Description = COALESCE(?, Description), Status = ?, Priority = COALESCE(?, Priority), AssigneeID = COALESCE(?, AssigneeID), StartDateTime = COALESCE(?, StartDateTime), DueDateTime = COALESCE(?, DueDateTime) WHERE TaskID = ?", 
                  (name, description, status, priority, assignee_id, start_datetime or None, due_datetime or None, task_id))
        conn.commit()
        conn.close()
        return redirect(url_for('project', project_id=project_id))
    c.execute("SELECT * FROM Tasks WHERE TaskID = ?", (task_id,))
    task = c.fetchone()
    c.execute("SELECT u.UserID, u.Name FROM Users u JOIN ProjectMembers pm ON u.UserID = pm.UserID WHERE pm.ProjectID = ?", (project_id,))
    users = c.fetchall()
    conn.close()
    return render_template('popup.html', action='edit_task', task=task, project_id=project_id, users=users)

@edit_task_bp.route('/project/<int:project_id>/delete_task/<int:task_id>', methods=['GET', 'POST'])
def delete_task(project_id, task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    current_user_id = session['user_id']
    if not check_role(current_user_id, project_id, ['Owner', 'Leader']):
        return jsonify({'error': 'Permission denied'}), 403
    if request.method == 'POST':
        conn = get_db()
        c = conn.cursor()
        c.execute("DELETE FROM Tasks WHERE TaskID = ?", (task_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('project', project_id=project_id))
    return render_template('popup.html', action='delete_task', project_id=project_id, task_id=task_id)