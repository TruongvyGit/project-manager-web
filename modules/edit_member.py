from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
import sqlite3

edit_member_bp = Blueprint('edit_member', __name__)

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

@edit_member_bp.route('/project/<int:project_id>/add_member', methods=['GET', 'POST'])
def add_member(project_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    current_user_id = session['user_id']
    if not check_role(current_user_id, project_id, ['Owner']):
        return jsonify({'error': 'Permission denied'}), 403
    if request.method == 'POST':
        user_id = request.form['user_id']
        role = request.form['role']
        if role == 'Owner':
            return jsonify({'error': 'Cannot assign Owner role to new member'}), 403
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO ProjectMembers (UserID, ProjectID, Role, JoinDate) VALUES (?, ?, ?, ?)", 
                  (user_id, project_id, role, '2025-03-28'))
        conn.commit()
        conn.close()
        return redirect(url_for('project', project_id=project_id))
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT UserID, Name FROM Users WHERE UserID NOT IN (SELECT UserID FROM ProjectMembers WHERE ProjectID = ?)", 
              (project_id,))
    users = c.fetchall()
    conn.close()
    return render_template('popup.html', action='add_member', project_id=project_id, users=users)

@edit_member_bp.route('/project/<int:project_id>/edit_member/<int:member_id>', methods=['POST'])
def edit_member(project_id, member_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    current_user_id = session['user_id']
    if not check_role(current_user_id, project_id, ['Owner']):
        return jsonify({'error': 'Permission denied'}), 403
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT UserID FROM ProjectMembers WHERE MemberID = ?", (member_id,))
    member = c.fetchone()
    if member and member['UserID'] == current_user_id:
        conn.close()
        return jsonify({'error': 'You cannot edit your own role'}), 403

    role = request.form['role']
    if role == 'Owner':
        conn.close()
        return jsonify({'error': 'Cannot change role to Owner'}), 403

    c.execute("UPDATE ProjectMembers SET Role = ? WHERE MemberID = ?", (role, member_id))
    conn.commit()
    conn.close()
    return redirect(url_for('project', project_id=project_id))

@edit_member_bp.route('/project/<int:project_id>/delete_member/<int:member_id>', methods=['GET', 'POST'])
def delete_member(project_id, member_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    current_user_id = session['user_id']
    if not check_role(current_user_id, project_id, ['Owner']):
        return jsonify({'error': 'Permission denied'}), 403
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT UserID FROM ProjectMembers WHERE MemberID = ?", (member_id,))
    member = c.fetchone()
    if member and member['UserID'] == current_user_id:
        conn.close()
        return jsonify({'error': 'You cannot delete yourself'}), 403

    if request.method == 'POST':
        c.execute("DELETE FROM ProjectMembers WHERE MemberID = ?", (member_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('project', project_id=project_id))
    return render_template('popup.html', action='delete_member', project_id=project_id, member_id=member_id)