from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション管理に必要（任意の文字列）

# メモリ上の仮ユーザー情報（あとでDBに変更もできる）
users = {}

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

        if username in users:
            return "そのユーザー名はすでに使われています", 400

        users[username] = password
        return f"登録完了！ようこそ、{username} さん"

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('todo'))
        else:
            return "ユーザー名またはパスワードが違います", 401

    return render_template('login.html')

@app.route('/todo')
def todo():
    if 'username' in session:
        return render_template('todo.html', username=session['username'])
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
