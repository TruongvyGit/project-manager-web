from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (name) VALUES ('Test User')")
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.commit()
    conn.close()
    return render_template('index.html', users=users)

if __name__ == '__main__':
    init_db()  # Khởi tạo database khi chạy lần đầu
    app.run(debug=True)