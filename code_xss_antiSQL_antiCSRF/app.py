from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import secrets
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

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
            session['csrf_tokens'] = {}
            session['csrf_token_expiry'] = int(time.time()) + 3600  # 1小时过期
            session['ip_address'] = request.remote_addr
            session['user_agent'] = request.headers.get('User-Agent')
            return redirect(url_for('index'))
        
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
    # 验证session基本完整性
    if not session.get('logged_in') or \
       not session.get('ip_address') or \
       not session.get('user_agent'):
        session.clear()
        return redirect(url_for('login'))
        
    # 检查IP和User-Agent是否匹配，不匹配则拒绝操作但保持登录
    ip_mismatch = session.get('ip_address') != request.remote_addr
    ua_mismatch = session.get('user_agent') != request.headers.get('User-Agent')
    
    # 如果IP或UA不匹配，拒绝操作但不登出
    if ip_mismatch or ua_mismatch:
        return render_template("index.html", query="", comments=dataset, csrf_token=session.get('csrf_tokens', {}).keys()[0] if session.get('csrf_tokens') else "", error_message="检测到可疑请求，操作已被拒绝")
        
    query = ""
    if request.method == "POST":
        if request.form.get("submit") == "提交新评论":
            csrf_token = request.form.get('csrf_token')
            # 增强CSRF token验证
            if not csrf_token or csrf_token not in session.get('csrf_tokens', {}) or \
               int(time.time()) > session.get('csrf_token_expiry', 0) or \
               session['csrf_tokens'].get(csrf_token) != True:
                return render_template("index.html", query="", comments=dataset, csrf_token=session.get('csrf_tokens', {}).keys()[0] if session.get('csrf_tokens') else "", error_message="无效的CSRF令牌，请刷新页面后重试")
            
            # 立即移除已使用的token
            session['csrf_tokens'].pop(csrf_token, None)
            
            comment = request.form.get("newComment").strip()
            if comment:
                dataset.append(comment)
                
            # 生成新的CSRF token
            csrf_token = secrets.token_hex(32)
            session['csrf_tokens'][csrf_token] = True
            session['csrf_token_expiry'] = int(time.time()) + 1800  # 30分钟过期
    elif request.method == "GET":
        if request.args.get("submit") == "提交":
            csrf_token = request.args.get('csrf_token')
            # 增强CSRF token验证
            if not csrf_token or csrf_token not in session.get('csrf_tokens', {}) or \
               int(time.time()) > session.get('csrf_token_expiry', 0) or \
               session['csrf_tokens'].get(csrf_token) != True:
                return render_template("index.html", query="", comments=dataset, csrf_token=session.get('csrf_tokens', {}).keys()[0] if session.get('csrf_tokens') else "", error_message="无效的CSRF令牌，请刷新页面后重试")
                
            # 立即移除已使用的token
            session['csrf_tokens'].pop(csrf_token, None)
            
            query = request.args.get("content").strip()
            if query:
                dataset.append(query)
    if not session.get('csrf_tokens'):
        session['csrf_tokens'] = {}
    # 生成更强的CSRF token并设置更短的过期时间
    csrf_token = secrets.token_hex(32)
    session['csrf_tokens'] = {csrf_token: True}  # 每次只保留最新token
    session['csrf_token_expiry'] = int(time.time()) + 300  # 5分钟过期
    return render_template("index.html", query=query, comments=dataset, csrf_token=csrf_token)


if __name__ == "__main__":
    init_db()
    app.run()