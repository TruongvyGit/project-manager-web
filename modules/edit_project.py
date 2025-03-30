from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
import sqlite3

edit_project_bp = Blueprint('edit_project', __name__)

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

@edit_project_bp.route('/create_project', methods=['GET', 'POST'])
def create_project():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    current_user_id = session['user_id']
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO Projects (ProjectName, Description, CreatorID) VALUES (?, ?, ?)", 
                  (name, description, current_user_id))
        project_id = c.lastrowid
        c.execute("INSERT INTO ProjectMembers (UserID, ProjectID, Role, JoinDate) VALUES (?, ?, 'Owner', ?)", 
                  (current_user_id, project_id, '2025-03-28'))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('popup.html', action='create_project')

@edit_project_bp.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    current_user_id = session['user_id']
    if not check_role(current_user_id, project_id, ['Owner']):
        return jsonify({'error': 'Permission denied'}), 403
    conn = get_db()
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        c.execute("UPDATE Projects SET ProjectName = ?, Description = ? WHERE ProjectID = ?", 
                  (name, description, project_id))
        conn.commit()
        conn.close()
        return redirect(url_for('project', project_id=project_id))
    c.execute("SELECT * FROM Projects WHERE ProjectID = ?", (project_id,))
    project = c.fetchone()
    conn.close()
    return render_template('popup.html', action='edit_project', project=project)

@edit_project_bp.route('/delete_project/<int:project_id>', methods=['GET', 'POST'])
def delete_project(project_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    current_user_id = session['user_id']
    if not check_role(current_user_id, project_id, ['Owner']):
        return jsonify({'error': 'Permission denied'}), 403
    if request.method == 'POST':
        conn = get_db()
        c = conn.cursor()
        c.execute("DELETE FROM ProjectMembers WHERE ProjectID = ?", (project_id,))
        c.execute("DELETE FROM Tasks WHERE ProjectID = ?", (project_id,))
        c.execute("DELETE FROM Projects WHERE ProjectID = ?", (project_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('popup.html', action='delete_project', project_id=project_id)