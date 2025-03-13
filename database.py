import sqlite3

def init_db():
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    # Tạo bảng users
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'member')''')
    try:
        c.execute('ALTER TABLE users ADD COLUMN email TEXT UNIQUE')
    except sqlite3.OperationalError:
        pass
    # Tạo bảng projects
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        created_by TEXT)''')
    # Tạo bảng tasks với liên kết project_id
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        assignee TEXT,
        due_date TEXT,
        project_id INTEGER,
        created_by TEXT,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY (project_id) REFERENCES projects(id))''')
    conn.commit()
    conn.close()

def add_user(username, password, role='member', email=None):
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

def get_user_role(username):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('SELECT role FROM users WHERE username = ?', (username,))
    role = c.fetchone()
    conn.close()
    return role[0] if role else None

def add_project(name, created_by):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('INSERT INTO projects (name, created_by) VALUES (?, ?)', 
              (name, created_by))
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
    c.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()

def add_task(title, assignee, due_date, project_id, created_by):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('INSERT INTO tasks (title, assignee, due_date, project_id, created_by) VALUES (?, ?, ?, ?, ?)', 
              (title, assignee, due_date, project_id, created_by))
    conn.commit()
    conn.close()

def get_tasks(project_id):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tasks WHERE project_id = ?', (project_id,))
    tasks = c.fetchall()
    conn.close()
    return tasks

def update_task(task_id, title, assignee, due_date, status):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('UPDATE tasks SET title = ?, assignee = ?, due_date = ?, status = ? WHERE id = ?', 
              (title, assignee, due_date, status, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

# Khởi tạo dữ liệu mẫu
if __name__ == "__main__":
    init_db()
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        add_user('admin', 'admin123', 'admin', 'admin@example.com')
        add_user('user1', 'pass123', 'member', 'user1@example.com')
    c.execute('SELECT COUNT(*) FROM projects')
    if c.fetchone()[0] == 0:
        add_project('Dự án mẫu 1', 'admin')
    conn.close()