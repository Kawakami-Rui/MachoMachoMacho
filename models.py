# db/models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class WorkoutLog(db.Model):
    __tablename__ = 'workout_logs'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)  # 記録日
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)  # 種目ID（外部キー）
    category = db.Column(db.String(100), nullable=False)  # カテゴリID（外部キー）
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)

    # 関連付け（リレーション）
    exercise = db.relationship('Exercise', backref=db.backref('logs', lazy=True))

    def __str__(self):
        return f"{self.date} - {self.exercise.name} : {self.sets}セット {self.reps}回 {self.weight}kg"