import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_migrate import Migrate

from db.models import db, Exercise

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
db_path = os.path.join(base_dir, 'db', 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# DB初期化
# ★SQLAlchemyをFlaskアプリにバインド
db.init_app(app)
# ★「flask_migrate」を使用できる様にする
migrate = Migrate(app, db)

# ==================================================
# 初期データ挿入
# ==================================================

def insert_initial_data():
    if Exercise.query.count() == 0:  # データベースに登録されたExerciseがまだ存在しない場合のみ
        initial_exercises = [
            Exercise(id=1, name='アームカール', category='腕', detail='上腕二頭筋', order=0),
            Exercise(id=2, name='トライセプスエクステンション', category='腕', detail='上腕三頭筋', order=1),
            Exercise(id=3, name='ベンチプレス', category='胸', detail='大胸筋', order=0),
            Exercise(id=4, name='プッシュアップ', category='胸', detail='大胸筋', order=1),
            Exercise(id=5, name='ショルダープレス', category='肩', detail='三角筋', order=0),
            Exercise(id=6, name='サイドレイズ', category='肩', detail='三角筋側部', order=1),
            Exercise(id=7, name='ラットプルダウン', category='背中', detail='広背筋', order=0),
            Exercise(id=8, name='デッドリフト', category='背中', detail='脊柱起立筋', order=1),
            Exercise(id=9, name='スクワット', category='脚', detail='大腿四頭筋', order=0),
            Exercise(id=10, name='レッグカール', category='脚', detail='ハムストリングス', order=1),
            Exercise(id=11, name='グルートブリッジ', category='その他', detail='大臀筋', order=0),
            Exercise(id=12, name='ネックフレクション', category='その他', detail='頸部筋群', order=1)
        ]
        db.session.add_all(initial_exercises)
        db.session.commit()

# ==================================================
# ルーティング
# ==================================================
# 種目一覧
@app.route('/')
def index():
    insert_initial_data()
    return render_template('index.html')

@app.route('/exercises', methods=['GET', 'POST'])
def exercise_settings():
    from collections import defaultdict, OrderedDict

    if request.method == 'POST':
        # クライアントから送られたJSONを取得して新しいExerciseを追加
        data = request.get_json()
        name = data.get('name')
        category = data.get('category')
        detail = data.get('detail')

        # 同じカテゴリ内での最大の並び順(order)を取得し、次の番号を設定
        max_order = db.session.query(db.func.max(Exercise.order)).filter_by(category=category).scalar() or 0
        new_ex = Exercise(name=name, category=category, detail=detail, order=max_order + 1)

        db.session.add(new_ex)
        db.session.commit()

        return jsonify({
            'id': new_ex.id,
            'name': new_ex.name,
            'detail': new_ex.detail,
            'category': new_ex.category
        }), 201
    

    # 種目リストをカテゴリごとにグループ化して順序を整える
    category_order = ['胸', '肩', '腕', '背中', '腹筋', '脚', 'その他']
    groups = defaultdict(list)

    for exercise in Exercise.query.order_by(Exercise.category, Exercise.order).all():
        groups[exercise.category].append(exercise)
    ordered_groups = OrderedDict()

    for category in category_order:
        ordered_groups[category] = groups[category]
        
    return render_template(
        'exercises_edit.html',
        grouped_exercises=ordered_groups
    )

@app.route('/exercises/<int:exercise_id>', methods=['DELETE'])
def delete_exercise(exercise_id):

    # 指定されたIDの種目を削除する
    exercise = Exercise.query.get_or_404(exercise_id)
    db.session.delete(exercise)
    db.session.commit()
    return '', 204

@app.route("/exercises/reorder", methods=["POST"])
def reorder_exercises():
    data = request.get_json()
    for item in data:
        exercise = Exercise.query.get(item["id"])
        if exercise:
            exercise.order = item["order"]
    db.session.commit()
    return jsonify({"status": "ok"})

# ==================================================
# 実行
# ==================================================


if __name__ == '__main__':
    app.run(port=5001, debug=True)