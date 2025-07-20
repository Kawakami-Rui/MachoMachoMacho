from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class PersonalInfo(db.Model):
    __tablename__ = 'personal_info'  # テーブル名

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    height = db.Column(db.String(10), nullable=True)
    weight = db.Column(db.String(10), nullable=True)

    def __str__(self):
        return f'ユーザー:{self.username}, メール:{self.email}, 身長:{self.height}, 体重:{self.weight}'
