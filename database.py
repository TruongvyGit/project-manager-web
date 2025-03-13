import sqlite3

def init_db():
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    # Bảng users
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'member')''')
    # Bảng tasks
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        assignee TEXT,
        due_date TEXT,
        created_by TEXT,
        status TEXT DEFAULT 'pending')''')
    conn.commit()
    conn.close()

def add_user(username, password, role='member'):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
              (username, password, role))
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

def add_task(title, assignee, due_date, created_by):
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('INSERT INTO tasks (title, assignee, due_date, created_by) VALUES (?, ?, ?, ?)', 
              (title, assignee, due_date, created_by))
    conn.commit()
    conn.close()

def get_tasks():
    conn = sqlite3.connect('project.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tasks')
    tasks = c.fetchall()
    conn.close()
    return tasks

# Thêm người dùng mẫu
if __name__ == "__main__":
    init_db()
    add_user('admin', 'admin123', 'admin')
    add_user('user1', 'pass123', 'member')