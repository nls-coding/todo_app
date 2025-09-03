import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# 本番は環境変数から読み込むのが安全（例: os.environ.get("SECRET_KEY")）
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key")

# セッションのセキュリティ
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# ===== SQLite 接続ユーティリティ =====
def get_db():
    conn = sqlite3.connect("todo_app.db")
    conn.row_factory = sqlite3.Row  # クエリ結果を辞書型で返す
    return conn

def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                task TEXT NOT NULL,
                FOREIGN KEY(username) REFERENCES users(username)
            )
        """)
        db.commit()

# ===== ルーティング =====
@app.route('/')
def index():
    return 'Hello, Flask!'

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if not username or not password:
            return "全ての項目を入力してください", 400

        with get_db() as conn:
            cur = conn.cursor()
            # 既存ユーザー確認
            cur.execute("SELECT 1 FROM users WHERE username = ?", (username,))
            if cur.fetchone():
                return "そのユーザー名はすでに使われています", 400

            # ★ 登録時にハッシュ化して保存 ★
            hashed_password = generate_password_hash(password)
            cur.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password),
            )
            conn.commit()

        return f"登録完了！ようこそ、{username} さん"

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        with get_db() as conn:
            cur = conn.cursor()
            # ★ ユーザー取得 → ハッシュ照合 ★
            cur.execute("SELECT username, password FROM users WHERE username = ?", (username,))
            user = cur.fetchone()

        if user and check_password_hash(user["password"], password):
            session["username"] = username
            return redirect(url_for("todo"))
        else:
            return "ユーザー名またはパスワードが違います", 401

    return render_template("login.html")

@app.route("/todo", methods=["GET", "POST"])
def todo():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]

    if request.method == "POST":
        task = request.form["task"].strip()
        if task:
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO tasks (username, task) VALUES (?, ?)",
                    (username, task),
                )
                conn.commit()
        return redirect(url_for("todo"))

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, task FROM tasks WHERE username = ? ORDER BY id DESC", (username,))
        tasks = cur.fetchall()

    return render_template("todo.html", username=username, tasks=tasks)

@app.route("/todo/delete/<int:task_id>")
def delete_task(task_id):
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    with get_db() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ? AND username = ?", (task_id, username))
        conn.commit()
    return redirect(url_for("todo"))

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
