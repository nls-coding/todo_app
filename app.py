import json
import os
from flask import Flask, request, session, redirect, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション管理に必要

tasks_json_path = r"tasks.json"
users_json_path = r"users.json"

# ---------- ユーザーデータの読み書き ----------
def load_users():
    try:
        with open(users_json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users():
    with open(users_json_path, 'w') as f:
        json.dump(users, f)

# ---------- タスクデータの読み書き ----------
def load_tasks():
    try:
        with open(tasks_json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_tasks():
    with open(tasks_json_path, 'w') as f:
        json.dump(tasks, f)


users = load_users()
tasks = load_tasks()



@app.route('/reload')
def reload_data():
    global users, tasks
    users = load_users()
    tasks = load_tasks()
    return "再読み込み完了"

# ---------- ルーティング ----------
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return "全ての項目を入力してください", 400

        if username in users:
            return "そのユーザー名はすでに使われています", 400

        hashed_password = generate_password_hash(password)  # パスワードをハッシュ化
        users[username] = hashed_password
        tasks[username] = []
        save_users()
        save_tasks()
        return f"登録完了！ようこそ、{username} さん"

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and check_password_hash(users[username], password):  # ハッシュと照合
            session['username'] = username
            return redirect(url_for('todo'))
        else:
            return "ユーザー名またはパスワードが違います", 401

    return render_template('login.html')

@app.route('/todo', methods=['GET', 'POST'])
def todo():
    if 'username' in session:
        username = session['username']
        
        if request.method == 'POST':
            task = request.form['task']
            if task:
                tasks[username].append(task)
                save_tasks()
            return redirect(url_for('todo'))
        
        return render_template('todo.html', username=username, tasks=tasks[username])
    else:
        return redirect(url_for('login'))

@app.route('/todo/delete/<int:task_id>')
def delete_task(task_id):
    if 'username' in session:
        username = session['username']
        if 0 <= task_id < len(tasks[username]):
            tasks[username].pop(task_id)
            save_tasks()
        return redirect(url_for('todo'))
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
