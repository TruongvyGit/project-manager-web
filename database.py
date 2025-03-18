import sqlite3

def init_db():
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user')''')
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        created_by TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS labels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        created_by TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS project_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        user_id INTEGER,
        project_role TEXT DEFAULT 'Member',
        status TEXT DEFAULT 'pending',
        FOREIGN KEY (project_id) REFERENCES projects(id),
        FOREIGN KEY (user_id) REFERENCES users(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        assignee TEXT,
        due_date TEXT,
        project_id INTEGER,
        label_id INTEGER,
        created_by TEXT,
        status TEXT DEFAULT 'todo',
        description TEXT,
        FOREIGN KEY (project_id) REFERENCES projects(id),
        FOREIGN KEY (label_id) REFERENCES labels(id))''')
    conn.commit()
    conn.close()

def add_user(username, password, role='user', email=None):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)', 
              (username, email, password, role))
    conn.commit()
    conn.close()

def get_user(username, password):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
              (username, password))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_username(username):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user

def get_all_users():
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('SELECT username FROM users')
    users = c.fetchall()
    conn.close()
    return [user[0] for user in users]

def add_project(name, created_by):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('INSERT INTO projects (name, created_by) VALUES (?, ?)', 
              (name, created_by))
    project_id = c.lastrowid
    user = get_user_by_username(created_by)
    c.execute('INSERT INTO project_members (project_id, user_id, project_role, status) VALUES (?, ?, ?, ?)', 
              (project_id, user[0], 'Leader', 'approved'))
    conn.commit()
    conn.close()
    return project_id

def add_project_member(project_id, username, project_role):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    user = get_user_by_username(username)
    if user:
        c.execute('INSERT INTO project_members (project_id, user_id, project_role, status) VALUES (?, ?, ?, ?)', 
                  (project_id, user[0], project_role, 'approved'))
    conn.commit()
    conn.close()

def get_projects():
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('SELECT * FROM projects')
    projects = c.fetchall()
    conn.close()
    return projects

def update_project(project_id, name):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('UPDATE projects SET name = ? WHERE id = ?', (name, project_id))
    conn.commit()
    conn.close()

def delete_project(project_id):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE project_id = ?', (project_id,))
    c.execute('DELETE FROM project_members WHERE project_id = ?', (project_id,))
    c.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()

def add_label(name, created_by):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO labels (name, created_by) VALUES (?, ?)', 
              (name, created_by))
    conn.commit()
    conn.close()

def get_labels():
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('SELECT * FROM labels')
    labels = c.fetchall()
    conn.close()
    return labels

def update_label(label_id, name):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('UPDATE labels SET name = ? WHERE id = ?', (name, label_id))
    conn.commit()
    conn.close()

def delete_label(label_id):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('UPDATE tasks SET label_id = NULL WHERE label_id = ?', (label_id,))
    c.execute('DELETE FROM labels WHERE id = ?', (label_id,))
    conn.commit()
    conn.close()

def add_task(title, assignee, due_date, project_id, label_id, created_by, description):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('INSERT INTO tasks (title, assignee, due_date, project_id, label_id, created_by, description) VALUES (?, ?, ?, ?, ?, ?, ?)', 
              (title, assignee, due_date, project_id, label_id, created_by, description))
    conn.commit()
    conn.close()

def get_tasks(project_id):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    if project_id is None:
        c.execute('SELECT t.*, l.name FROM tasks t LEFT JOIN labels l ON t.label_id = l.id')
    else:
        c.execute('SELECT t.*, l.name FROM tasks t LEFT JOIN labels l ON t.label_id = l.id WHERE t.project_id = ?', 
                  (project_id,))
    tasks = c.fetchall()
    conn.close()
    return tasks

def update_task(task_id, title, assignee, due_date, label_id, status, description):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('UPDATE tasks SET title = ?, assignee = ?, due_date = ?, label_id = ?, status = ?, description = ? WHERE id = ?', 
              (title, assignee, due_date, label_id, status, description, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

def get_user_role(username):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('SELECT role FROM users WHERE username = ?', (username,))
    role = c.fetchone()
    conn.close()
    return role[0] if role else None

def get_project_role(project_id, username):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    user = get_user_by_username(username)
    c.execute('SELECT project_role FROM project_members WHERE project_id = ? AND user_id = ? AND status = "approved"', 
              (project_id, user[0]))
    role = c.fetchone()
    conn.close()
    return role[0] if role else None

def request_join_project(project_id, username):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    user = get_user_by_username(username)
    c.execute('INSERT INTO project_members (project_id, user_id, project_role, status) VALUES (?, ?, ?, ?)', 
              (project_id, user[0], 'Member', 'pending'))
    conn.commit()
    conn.close()

def get_pending_requests(project_id):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('SELECT pm.*, u.username FROM project_members pm JOIN users u ON pm.user_id = u.id WHERE pm.project_id = ? AND pm.status = "pending"', 
              (project_id,))
    requests = c.fetchall()
    conn.close()
    return requests

def approve_member(request_id):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('UPDATE project_members SET status = "approved" WHERE id = ?', (request_id,))
    conn.commit()
    conn.close()

def remove_member(project_id, user_id):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('DELETE FROM project_members WHERE project_id = ? AND user_id = ?', (project_id, user_id))
    conn.commit()
    conn.close()

def update_member_role(project_id, user_id, project_role):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('UPDATE project_members SET project_role = ? WHERE project_id = ? AND user_id = ?', 
              (project_role, project_id, user_id))
    conn.commit()
    conn.close()

def get_project_members(project_id):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('SELECT pm.*, u.username FROM project_members pm JOIN users u ON pm.user_id = u.id WHERE pm.project_id = ? AND pm.status = "approved"', 
              (project_id,))
    members = c.fetchall()
    conn.close()
    return members

def get_my_projects(username):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('SELECT p.* FROM projects p WHERE p.created_by = ?', (username,))
    projects = c.fetchall()
    conn.close()
    return projects

def get_joined_projects(username):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    user = get_user_by_username(username)
    c.execute('SELECT p.* FROM projects p JOIN project_members pm ON p.id = pm.project_id WHERE pm.user_id = ? AND pm.status = "approved" AND p.created_by != ?', 
              (user[0], username))
    projects = c.fetchall()
    conn.close()
    return projects

if __name__ == "__main__":
    init_db()
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        add_user('admin', 'admin123', 'admin', 'admin@example.com')
        add_user('user1', 'pass123', 'user', 'user1@example.com')
    c.execute('SELECT COUNT(*) FROM projects')
    if c.fetchone()[0] == 0:
        add_project('Dự án mẫu 1', 'admin')
    c.execute('SELECT COUNT(*) FROM labels')
    if c.fetchone()[0] == 0:
        add_label('Quan trọng', 'admin')
        add_label('Khẩn cấp', 'admin')
    conn.close()