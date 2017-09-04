from datetime import datetime
from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from .forms import LoginForm, EditForm
from .models import User

@app.before_request
def before_request():
    # 全局变量 current_user 是被 Flask-Login 设置
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.now()
        db.session.add(g.user)
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = g.user
    posts = [
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },{
            'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool'
        }
    ]
    return render_template('index.html',
        title = 'Home',
        user = user,
        posts = posts)


@app.route('/login/<nickname>', methods=['GET'])
def login_test(nickname):
    '''
    用于测试
    '''
    user = User.query.filter_by(nickname=nickname).first()
    if not user:
        flash('Error')
        return redirect(url_for('login'))
    logout_user()
    login_user(user, remember=True)
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    '''
    oid.loginhandle 告诉 Flask-OpenID 这是我们的登录视图函数。
    '''
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        # 触发用户使用 Flask-OpenID 认证
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])   # 
        # OpenID 认证异步发生。如果认证成功的话，Flask-OpenID 将会调用一个注册了 oid.after_login 装饰器的函数。如果失败的话，用户将会回到登陆页面。
    return render_template('login.html',
                            title = 'Sign In',
                            form = form,
                            providers = app.config['OPENID_PROVIDERS'])


@lm.user_loader
def load_user(id):
    '''
    在 Flask-Login 中的用户 id 是字符串，因此在我们把 id 发送给 Flask-SQLAlchemy 之前，把 id 转成整型
    '''
    return User.query.get(int(id))


@oid.after_login
def after_login(resp):
    '''
    Flask-OpenID 登录回调
    resp 参数传入给 after_login 函数，它包含了从 OpenID 提供商返回来的信息。
    '''
    if resp.email is None or resp.email == '':
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    # 从数据库中搜索邮箱地址。如果邮箱地址不在数据库中，添加一个新用户到数据库。
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == '':
            nickname = resp.email.split('@')[0]
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    # 在 next 页没有提供的情况下，我们会重定向到首页，否则会重定向到 next 页
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/logout')
def logout():
    '''
    登出
    '''
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<nickname>')
@login_required
def user(nickname):
    '''
    用户详情页
    需要登录
    '''
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    posts = [
        { 'author': user, 'body': 'Test post #1' },
        { 'author': user, 'body': 'Test post #2' }
    ]
    return render_template('user.html',
        user = user,
        posts = posts)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)
