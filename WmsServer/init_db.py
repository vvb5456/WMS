"""初始化数据库表和种子数据。用法: python init_db.py"""
from app import create_app, seed_data
from app.extensions import db

app = create_app()

with app.app_context():
    db.create_all()
    seed_data()
    print("数据库初始化完成。默认账号: admin / keeper / viewer，密码均为 admin123")
