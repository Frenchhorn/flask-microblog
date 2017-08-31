"""
使用`env\Scripts\python run.py`来启动开发服务器
"""
import os
from app import app, db
from config import SQLALCHEMY_DATABASE_URI


if not os.path.exists(SQLALCHEMY_DATABASE_URI):
    db.create_all()

app.run(debug=True)