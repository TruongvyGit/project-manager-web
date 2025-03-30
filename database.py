import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('project_management.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Xóa dữ liệu cũ (nếu có) trước khi tạo bảng
    c.execute("DROP TABLE IF EXISTS Tasks")
    c.execute("DROP TABLE IF EXISTS ProjectMembers")
    c.execute("DROP TABLE IF EXISTS Projects")
    c.execute("DROP TABLE IF EXISTS Users")

    # Tạo bảng Users
    c.execute('''CREATE TABLE Users (
        UserID INTEGER PRIMARY KEY AUTOINCREMENT,
        Username VARCHAR(50) UNIQUE NOT NULL,
        Name VARCHAR(100) NOT NULL,
        Email VARCHAR(100) UNIQUE NOT NULL,
        Password VARCHAR(255) NOT NULL,
        CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Tạo bảng Projects
    c.execute('''CREATE TABLE Projects (
        ProjectID INTEGER PRIMARY KEY AUTOINCREMENT,
        ProjectName VARCHAR(255) NOT NULL,
        Description TEXT,
        CreatorID INTEGER NOT NULL,
        FOREIGN KEY (CreatorID) REFERENCES Users(UserID)
    )''')

    # Tạo bảng ProjectMembers
    c.execute('''CREATE TABLE ProjectMembers (
        MemberID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER NOT NULL,
        ProjectID INTEGER NOT NULL,
        Role TEXT CHECK(Role IN ('Owner', 'Leader', 'Member')) NOT NULL,
        JoinDate DATE,
        UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (UserID) REFERENCES Users(UserID),
        FOREIGN KEY (ProjectID) REFERENCES Projects(ProjectID),
        UNIQUE (UserID, ProjectID)
    )''')

    # Tạo bảng Tasks
    c.execute('''CREATE TABLE Tasks (
        TaskID INTEGER PRIMARY KEY AUTOINCREMENT,
        TaskName VARCHAR(255) NOT NULL,
        Description TEXT,
        Status TEXT CHECK(Status IN ('Not Started', 'In Progress', 'Completed', 'On Hold')) DEFAULT 'Not Started',
        Priority TEXT CHECK(Priority IN ('Low', 'Medium', 'High', 'Urgent')) DEFAULT 'Medium',
        StartDateTime DATETIME,
        DueDateTime DATETIME,
        AssigneeID INTEGER,
        CreatorID INTEGER,
        ProjectID INTEGER,
        EstimatedTime INTEGER,
        ActualTime INTEGER,
        CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (AssigneeID) REFERENCES Users(UserID),
        FOREIGN KEY (CreatorID) REFERENCES Users(UserID),
        FOREIGN KEY (ProjectID) REFERENCES Projects(ProjectID)
    )''')

    # Thêm dữ liệu mẫu
    # 1. Thêm 5 user
    users = [
        ('u1', 'User 1', 'user1@gmail.com', '111'),
        ('u2', 'User 2', 'user2@gmail.com', '111'),
        ('u3', 'User 3', 'user3@gmail.com', '111'),
        ('u4', 'User 4', 'user4@gmail.com', '111'),
        ('u5', 'User 5', 'user5@gmail.com', '111'),
    ]
    c.executemany("INSERT INTO Users (Username, Name, Email, Password) VALUES (?, ?, ?, ?)", users)

    # 2. Mỗi user tạo 3 project
    projects = []
    for i in range(1, 6):  # u1 đến u5
        for j in range(1, 4):  # 3 project mỗi user
            projects.append((f"Project {j}_u{i}", f"Description for Project {j}_u{i}", i))
    c.executemany("INSERT INTO Projects (ProjectName, Description, CreatorID) VALUES (?, ?, ?)", projects)

    # 3. Thêm members vào mỗi project
    project_members = []
    for project_id in range(1, 16):  # 15 projects (5 user x 3 project)
        creator_id = (project_id - 1) // 3 + 1  # Xác định CreatorID (u1 -> 1, u2 -> 2,...)
        project_members.append((creator_id, project_id, 'Owner', '2025-03-30'))
        other_users = [u for u in range(1, 6) if u != creator_id]
        project_members.append((other_users[0], project_id, 'Leader', '2025-03-30'))
        project_members.append((other_users[1], project_id, 'Member', '2025-03-30'))
        project_members.append((other_users[2], project_id, 'Member', '2025-03-30'))
    c.executemany("INSERT INTO ProjectMembers (UserID, ProjectID, Role, JoinDate) VALUES (?, ?, ?, ?)", project_members)

    # 4. Thêm 10 task cho mỗi project
    tasks = []
    for project_id in range(1, 16):
        c.execute("SELECT UserID FROM ProjectMembers WHERE ProjectID = ? AND Role IN ('Leader', 'Member')", (project_id,))
        members = [row['UserID'] for row in c.fetchall()]
        creator_id = (project_id - 1) // 3 + 1
        for task_num in range(1, 11):
            assignee_id = members[(task_num - 1) % 3]
            tasks.append((
                f"Task {task_num} of Project {project_id}", 
                f"Description for Task {task_num}", 
                'Not Started', 
                'Medium', 
                None, None, 
                assignee_id, 
                creator_id, 
                project_id, 
                5, None
            ))
    c.executemany("INSERT INTO Tasks (TaskName, Description, Status, Priority, StartDateTime, DueDateTime, AssigneeID, CreatorID, ProjectID, EstimatedTime, ActualTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", tasks)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()