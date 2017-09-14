import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_openid import OpenID
from flask_mail import Mail
from flask_babel import Babel, lazy_gettext
from config import basedir
from .momentjs import momentjs


app = Flask(__name__)
app.config.from_object('config')

# 数据库 ORM
db = SQLAlchemy(app)

# 日志
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.login_message = lazy_gettext('Please log in to access this page.')   # lazy_gettext，不会立即翻译，会推迟翻译直到字符串实际上被使用的时候。

# openID认证
oid = OpenID(app, os.path.join(basedir, 'tmp'))

# 用于发送邮件
mail = Mail(app)

# 处理日期的 Javascript 框架
app.jinja_env.globals['momentjs'] = momentjs

# I18n
babel = Babel(app)

from app import views, models

# if not app.debug:
if True:
    '''
    通过email发生错误信息
    开启测试邮箱服务器
    python -m smtpd -n -c DebuggingServer localhost:25
    '''
    from config import ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
    import logging
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'microblog failure', credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
    # app.logger.error('testtest')

    '''
    保存到日志文件
    '''
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/microblog.log', 'a', 1*1024*1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    # app.logger.info('microblog startup')
