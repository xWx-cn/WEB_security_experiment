# WEB_security_experiment
## brief introduction
this project includes five version, each has different vulnerability and defense level.    

## procedure
1.实现反射型XSS、存储型XSS攻击(code_unsafe)    
Flask应用存在两个XSS漏洞：    
(1)反射型XSS：通过查询参数content传入恶意脚本，如<script>alert('reflected XSS')</script>，由于使用了{{query|safe}}直接输出未过滤内容，脚本会被执行。    
(2)存储型XSS：通过newComment提交恶意脚本，<script>alert('Stored XSS')</script> ，该内容会被存入dataset数组并在后续页面加载时通过{{comment|safe}}执行。    
实验方法：    
①反射型XSS测试：在搜索框输入<script>alert('reflected XSS')</script> 并提交    
②存储型XSS测试：在评论框输入<script>alert('Stored XSS')</script>并提交，刷新页面后脚本仍会执行    
    
2.使用字符转换防御XSS攻击(code_antixss)    
(1)在app.py中添加了全角字符转换功能，将用户输入中的半角字符转换为全角字符    
(2)移除了index.html模板中的|safe过滤器，防止直接渲染HTML代码    
    
3.新增登录功能。(code_antixss)    
设计有SQL 注入隐患的代码，进行攻击并防范    
(1)修改app.py文件添加SQLite数据库连接和用户表，实现不安全的SQL查询逻辑。    
(2)修改index.html文件添加登录表单。可以通过输入特殊字符如单引号来实现SQL注入攻击，例如在用户名输入:admin' --，可以绕过密码验证。    
  
(3)修改代码防范SQL攻击：(code_antixss_antiSQL)    
代码中的SQL注入漏洞主要存在于登录功能的SQL查询语句拼接方式。修改app.py中的登录逻辑，使用参数化查询来防范SQL注入攻击。    
     
4.实现CSRF并防御     
(code_xss_antiSQL_CSRF)    
（1）修改index.html代码，使用safe过滤器渲染XSS脚本，并实现CSRF：①在浏览器中登录信任网站A；②通过验证在浏览器中产生cookie；③用户在没有登出A的情况下访问恶意网站B；④网站B发送一个访问网站A的请求；⑤根据网站B在④中的请求，浏览器带着②中产生的cookie访问A。     
创建了恶意网页malicious.html，包含自动提交表单到原网站的代码，利用用户已登录状态发起CSRF攻击。恶意网页会通过JavaScript自动提交伪造请求到原网站的评论接口，当用户访问恶意网站时，会触发XSS攻击脚本。    
    
实现：
①登录原网站获取cookie；②http://127.0.0.1:5000/malicious访问恶意网站malicious.html；③ 恶意网站自动提交表单到原网站；④原网站接收请求并执行XSS脚本。    
    
(code_xss_antiSQL_antiCSRF)    
（2）修改代码防御CSRF：    
1)使用SameSite Cookie属性阻止第三方请求     
2)为每个表单生成唯一CSRF token    
3)严格验证token与session的匹配关系     
4)设置token过期时间     
5) 绑定IP和User-Agent增强安全性。这些措施主要在app.py的session管理和token验证逻辑中实现。    
此时仍存在XSS漏洞。但无法实现CSRF       
