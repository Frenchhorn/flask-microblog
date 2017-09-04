from app import db
from app.models import User, Post
u = User('test', 'test@test.com')
u2 = User('test2', 'test2@test.com')
p = Post('post1', u)
p2 = Post('post2', u)
p3 = Post('post3', u2)
db.session.add(u)
db.session.add(u2)
db.session.add(p)
db.session.add(p2)
db.session.add(p3)
db.session.commit()

