import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__) #Flask() は クラス 
app.secret_key = 'your_secret_key'

# SQLiteデータベース接続
def get_db():
    conn = sqlite3.connect('todo_app.db') #SQLiteデータベースファイルに接続
    conn.row_factory = sqlite3.Row  # クエリ結果を辞書型で返す
    return conn

# 初期化
def init_db():
    with get_db() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY, 
            password TEXT NOT NULL)''')
        db.execute('''CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username TEXT NOT NULL, 
            task TEXT NOT NULL, 
            FOREIGN KEY(username) REFERENCES users(username))''')
        db.commit()

@app.route('/')
def index():
    return 'Hello, Flask!'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return "全ての項目を入力してください", 400

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            return "そのユーザー名はすでに使われています", 400

        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return f"登録完了！ようこそ、{username} さん"

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        if cursor.fetchone():
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
                conn = get_db()
                conn.execute('INSERT INTO tasks (username, task) VALUES (?, ?)', (username, task))
                conn.commit()
            return redirect(url_for('todo'))  # リダイレクトしてタスクが更新されたページを表示
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE username = ?', (username,))
        tasks = cursor.fetchall()
        
        return render_template('todo.html', username=username, tasks=tasks)
    else:
        return redirect(url_for('login'))

@app.route('/todo/delete/<int:task_id>')
def delete_task(task_id):
    if 'username' in session:
        username = session['username']
        conn = get_db()
        conn.execute('DELETE FROM tasks WHERE id = ? AND username = ?', (task_id, username))
        conn.commit()
        return redirect(url_for('todo'))
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()  # データベースの初期化
    app.run(debug=True)
