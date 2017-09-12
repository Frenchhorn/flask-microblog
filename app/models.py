from datetime import datetime
from app import db


# 辅助表
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nickname = db.Column(db.String(64), index = True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    followed = db.relationship('User',  # User 是关系中的右边的表(实体)。因为定义一个自我指向的关系，我们在两边使用同样的类。
        secondary = followers,  # secondary 指明了用于这种关系的辅助表。
        primaryjoin = (followers.c.follower_id == id),  # primaryjoin 表示辅助表中连接左边实体(发起关注的用户)的条件。注意因为 followers 表不是一个模式，获得字段名的语法有些怪异。
        secondaryjoin = (followers.c.followed_id == id),    # secondaryjoin 表示辅助表中连接右边实体(被关注的用户)的条件。
        backref = db.backref('followers', lazy='dynamic'),  # backref 定义这种关系将如何从右边实体进行访问。
        lazy = 'dynamic')

    def __init__(self, nickname, email):
        self.nickname = nickname
        self.email = email
        self.about_me = ''
        self.last_seen = datetime.utcnow()


    def __repr__(self):
        return '<User %r>' % (self.nickname)

    def avatar(self, size):
        # 返回头像
        size = str(size)
        return 'https://unsplash.it/'+size+'/'+size+'/?random'

    @staticmethod
    def make_unique_nickname(nickname):
        # 使用OpenID回调，创建用户时验证nickname是否已存在
        if User.query.filter_by(nickname=nickname).first() == None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=nickname).first() == None:
                break
            version += 1
        return new_nickname

    def follow(self, user):
        # 关注某用户
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        # 取消关注
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        # 做一个 followed 关系查询，这个查询返回所有当前用户作为关注者的 (follower, followed) 对，再进行筛选。
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        # 登录用户所有关注者撰写的 blog ,按时间排序。
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

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

>>> results = Post.query.filter(Post.body=='post1')
>>> results = Post.query.filter(Post.body.like('%post%'))
>>> results = Post.query.filter_by(body='post1')
'''