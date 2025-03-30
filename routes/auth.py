from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3

auth_bp = Blueprint('auth', __name__)

def get_db():
    conn = sqlite3.connect('project_management.db')
    conn.row_factory = sqlite3.Row
    return conn

@auth_bp.route('/login', methods=['GET', 'POST'])
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
            return redirect(url_for('auth.login'))
        if user['Password'] != password:
            flash("Mật khẩu không đúng")
            return redirect(url_for('auth.login'))
        
        session['user_id'] = user['UserID']
        session['username'] = user['Username']
        return redirect(url_for('index.index'))  # Sửa từ 'index' thành 'index.index'
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
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
            return redirect(url_for('auth.register'))
        c.execute("SELECT * FROM Users WHERE Email = ?", (email,))
        if c.fetchone():
            flash("Email đã tồn tại")
            return redirect(url_for('auth.register'))
        if password != confirm_password:
            flash("Mật khẩu không khớp")
            return redirect(url_for('auth.register'))
        
        c.execute("INSERT INTO Users (Username, Name, Email, Password) VALUES (?, ?, ?, ?)", 
                  (username, name, email, password))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        
        session['user_id'] = user_id
        session['username'] = username
        return redirect(url_for('index.index'))  # Sửa từ 'index' thành 'index.index'
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('auth.login'))