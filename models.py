
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
    
class WorkoutLog(db.Model):
    __tablename__ = 'workout_logs'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    sets = db.Column(db.Integer, nullable=True)
    reps = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    category = db.Column(db.String(100), nullable=False)

    exercise = db.relationship('Exercise', backref='logs')

    def __str__(self):
        return f'記録日：{self.date} 種目名：{self.exercise.name}（カテゴリ：{self.category}） {self.sets}セット×{self.reps}回 {self.weight}kg'