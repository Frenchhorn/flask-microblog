from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)

    def __init__(self, nickname, email):
        self.nickname = nickname
        self.email = email

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    # Flask-Login 扩展需要在我们的 User 类中实现一些特定的方法。
    def is_authenticated(self):
        '''
        is_authenticated 方法有一个具有迷惑性的名称。一般而言，这个方法应该只返回 True，除非表示用户的对象因为某些原因不允许被认证。
        '''
        return True

    def is_active(self):
        '''
        is_active 方法应该返回 True，除非是用户是无效的，比如因为他们的账号是被禁止。
        '''
        return True

    def is_anonymous(self):
        '''
        is_anonymous 方法应该返回 True，除非是匿名的用户不允许登录系统。
        '''
        return False

    def get_id(self):
        '''
        get_id 方法应该返回一个用户唯一的标识符，以 unicode 格式。
        '''
        return str(self.id)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',
        backref=db.backref('posts', lazy='dynamic'))

    timestamp = db.Column(db.DateTime)

    def __init__(self, body, user, timestamp=None):
        self.body = body
        if timestamp is None:
            timestamp = datetime.utcnow()
        self.timestamp = timestamp
        self.user = user

    def __repr__(self):
        return '<Post %r>' % (self.body)


'''
>>> py = User('Python', 'abc@asdf.com')
>>> p = Post('Hello Python!', py)
>>> db.session.add(py)
>>> db.session.add(p)
>>> db.session.commit()

>>> user = User.query.get(1)
>>> users = User.query.all()
>>> user.posts.all()
>>> User.query.order_by('nickname desc').all()
>>> post = Post.query.get(1)
>>> post.user.query.get(1)
'''