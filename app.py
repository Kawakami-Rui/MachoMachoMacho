import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# ==================================================
# インスタンス生成
# ==================================================
app = Flask(__name__)

# ==================================================
# Flaskに対する設定
# ================================================== 
    
# 秘密鍵設定（セッション保護などに使用）
app.config['SECRET_KEY'] = os.urandom(24)

base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# DB初期化
# ★db変数を使用してSQLAlchemyを操作できる
db = SQLAlchemy(app)
# ★「flask_migrate」を使用できる様にする
migrate = Migrate(app, db)

#==================================================
# モデル
#==================================================
class Exercise(db.Model):
    # テーブル名
    __tablename__ = 'exercises'
    
    # 種目ID
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 筋トレ種目名
    name = db.Column(db.String(200), nullable=False)
    # カテゴリ（部位）
    category = db.Column(db.String(100), nullable=False)
    # 詳細な筋肉部位
    detail = db.Column(db.String(200), nullable=True)

    # 表示用
    def __str__(self):
        return f'種目ID：{self.id} 種目名：{self.name} カテゴリ：{self.category} 詳細：{self.detail}'

def insert_initial_data():
    if Exercise.query.count() == 0:
        initial_exercises = [
            Exercise(name='アームカール', category='腕', detail='上腕二頭筋'),
            Exercise(name='トライセプスエクステンション', category='腕', detail='上腕三頭筋'),
            Exercise(name='ベンチプレス', category='胸', detail='大胸筋'),
            Exercise(name='プッシュアップ', category='胸', detail='大胸筋'),
            Exercise(name='ショルダープレス', category='肩', detail='三角筋'),
            Exercise(name='サイドレイズ', category='肩', detail='三角筋側部'),
            Exercise(name='ラットプルダウン', category='背中', detail='広背筋'),
            Exercise(name='デッドリフト', category='背中', detail='脊柱起立筋'),
            Exercise(name='スクワット', category='脚', detail='大腿四頭筋'),
            Exercise(name='レッグカール', category='脚', detail='ハムストリングス'),
            Exercise(name='グルートブリッジ', category='その他', detail='大臀筋'),
            Exercise(name='ネックフレクション', category='その他', detail='頸部筋群')
        ]
        db.session.bulk_save_objects(initial_exercises)
        db.session.commit()

# ==================================================
# ルーティング
# ==================================================
# 種目一覧
@app.route('/')
def index():
    insert_initial_data()
    # カテゴリごとに取得
    exercises_arm = Exercise.query.filter_by(category='腕').all()
    exercises_chest = Exercise.query.filter_by(category='胸').all()
    exercises_shoulder = Exercise.query.filter_by(category='肩').all()
    exercises_back = Exercise.query.filter_by(category='背中').all()
    exercises_leg = Exercise.query.filter_by(category='脚').all()
    exercises_abs = Exercise.query.filter_by(category='腹筋').all()
    exercises_other = Exercise.query.filter_by(category='その他').all()
    categories = ['胸', '肩', '腕', '背中', '腹筋', '脚', 'その他']
    return render_template(
        'index.html',
        exercises_arm=exercises_arm,
        exercises_chest=exercises_chest,
        exercises_shoulder=exercises_shoulder,
        exercises_back=exercises_back,
        exercises_leg=exercises_leg,
        exercises_abs=exercises_abs,
        exercises_other=exercises_other,
        categories=categories
    )

# 種目の追加
@app.route('/new', methods=['GET', 'POST'])
def new_exercise():
    # POST
    if request.method == 'POST':
        # 入力値取得
        name = request.form['name']
        category = request.form['category']
        detail = request.form['detail']
        exercise = Exercise(name=name, category=category, detail=detail)
        # 登録
        db.session.add(exercise)
        db.session.commit()
        # 一覧へ
        return redirect(url_for('index'))
    # GET
    return render_template('new_exercise.html')

# 種目の削除
@app.route('/delete/<int:exercise_id>')
def delete_exercise(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    db.session.delete(exercise)
    db.session.commit()
    return redirect(url_for('index'))

# ==================================================
# 実行
# ==================================================


if __name__ == '__main__':
    app.run(port=5001, debug=True)