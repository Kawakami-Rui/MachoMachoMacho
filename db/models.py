# db/models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Exercise(db.Model):
    __tablename__ = 'exercises'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    detail = db.Column(db.String(200), nullable=True)
    order = db.Column(db.Integer, nullable=True)

    def __str__(self):
        return f'種目ID：{self.id} 種目名：{self.name} カテゴリ：{self.category} 詳細：{self.detail}'
