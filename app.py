from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Cấu hình cơ sở dữ liệu SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Khởi tạo SQLAlchemy
db = SQLAlchemy(app)

# Định nghĩa mô hình User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'

# Tạo bảng khi ứng dụng khởi động
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    # Thêm dữ liệu mẫu (Test User) nếu chưa có
    if User.query.count() == 0:
        new_user = User(name='Test User')
        db.session.add(new_user)
        db.session.commit()
    
    # Lấy tất cả user
    users = User.query.all()
    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)