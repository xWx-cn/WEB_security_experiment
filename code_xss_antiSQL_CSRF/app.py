from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

dataset=["BIT网络安全课程真有趣","Web安全演示实验打卡","祝同学们都能取得好成绩!"]

# 初始化数据库
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT NOT NULL,
                 password TEXT NOT NULL)''')
    # 添加测试用户
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('admin', 'password123')")
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('username1', 'password1')")
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('username2', 'password2')")
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('username3', 'password3')")
    conn.commit()
    conn.close()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 使用参数化查询防止SQL注入
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return '登录失败，用户名或密码错误'
    
    return '''
        <form method="post">
            用户名: <input type="text" name="username"><br>
            密码: <input type="password" name="password"><br>
            <input type="submit" value="登录">
        </form>
    '''

@app.route('/malicious')
def malicious():
    return render_template('malicious.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    query = ""
    if request.method == "POST":
        if request.form.get("submit") == "提交新评论":
            comment = request.form.get("newComment").strip()
            print(type(comment))
            if comment:
                dataset.append(comment)
    elif request.method == "GET":
        if request.args.get("submit") == "提交":
            query = request.args.get("content").strip()
            if query:
                dataset.append(query)
                return render_template("index.html", query=query, comments=dataset)
        elif request.args.get("content"):
            query = request.args.get("content")
            dataset.append(query)
            return render_template("index.html", query=query, comments=dataset)
    return render_template("index.html", query=query, comments=dataset)


if __name__ == "__main__":
    init_db()
    app.run()