from flask_sqlalchemy import SQLAlchemy
# SQLAlchemyのインスタンスを生成
db = SQLAlchemy()

class PersonalInfo(db.Model):
    __tablename__ = 'personal_info'  # テーブル名
    ### db.Colummでpersonal_infoテーブルの設計図###

    id = db.Column(db.Integer, primary_key=True) #自動でIDを設定。
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    height = db.Column(db.String(10), nullable=True)
    weight = db.Column(db.String(10), nullable=True)
    difficulty = db.Column(db.String(20), nullable=True)       # 難易度
    custom_number = db.Column(db.Float, nullable=True)


    exercises = db.relationship('Exercise', backref='user', lazy=True)

    workout_logs = db.relationship('WorkoutLog', backref='user', lazy=True)


    def __str__(self):
        return f'ユーザー:{self.username}, メール:{self.email}, 身長:{self.height}, 体重:{self.weight}'


# 種目（エクササイズ）テーブルのモデル
class Exercise(db.Model):
    __tablename__ = 'exercises'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # ID
    name = db.Column(db.String(200), nullable=False)                  # 種目名（例：ベンチプレス）
    category = db.Column(db.String(100), nullable=False)              # カテゴリ（例：胸、脚）
    detail = db.Column(db.String(200), nullable=True)                 # 補足説明（省略可能）
    order = db.Column(db.Integer, nullable=True)                      # 表示順（並び替え用）
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)  # 論理削除フラグ
    user_id = db.Column(db.Integer, db.ForeignKey('personal_info.id'), nullable=False)

    def __str__(self):
        return f'種目ID：{self.id} 種目名：{self.name} カテゴリ：{self.category} 詳細：{self.detail}'

    def mark_as_deleted(self):
        self.is_deleted = True




# トレーニング記録（ワークアウトログ）テーブルのモデル
class WorkoutLog(db.Model):
    __tablename__ = 'workout_logs'

    id = db.Column(db.Integer, primary_key=True)                 # ID
    date = db.Column(db.Date, nullable=False)                    # トレーニング実施日
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)  # 種目ID（外部キー）
    user_id = db.Column(db.Integer, db.ForeignKey('personal_info.id'), nullable=False)  # 外部キー
    sets = db.Column(db.Integer, nullable=True)                  # セット数
    reps = db.Column(db.Integer, nullable=True)                  # レップ数
    weight = db.Column(db.Float, nullable=True)                  # 使用重量（kg）
    comment = db.Column(db.String(500), nullable=True) 

    # Exerciseとのリレーション設定（論理削除されていないもののみ取得）
    exercise = db.relationship('Exercise', viewonly=True)

    def __str__(self):
        return f'記録日：{self.date} 種目名：{self.exercise.name}（カテゴリ：{self.exercise.category}） {self.sets}セット×{self.reps}回 {self.weight}kg'