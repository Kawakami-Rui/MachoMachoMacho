import os
import datetime
import calendar
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_migrate import Migrate
from collections import defaultdict, OrderedDict

from models import db, Exercise, WorkoutLog

# Flaskアプリケーションの初期化
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

def get_grouped_exercises():
    """種目をカテゴリごとにグループ化し、並び順でソートして返す"""
    all_exercises = Exercise.query.filter_by(is_deleted=False).order_by(Exercise.category, Exercise.order).all() #Exerciseから全ての種目を取得し、カテゴリと表示順でソート
    category_order = ['胸', '肩', '腕', '背中', '腹筋', '脚', 'その他'] # カテゴリの表示順を固定
    groups = defaultdict(list)
    for ex in all_exercises:
        groups[ex.category].append(ex)

    ordered_groups = OrderedDict()
    for cat in category_order:
        # 空でも表示するように必ずセット
        ordered_groups[cat] = groups.get(cat, [])  # 存在しなければ空リスト
    return ordered_groups

# ========================================
# トップページ "/" → 今日の年月へリダイレクト
# ========================================
@app.route('/')

def index():
    insert_initial_data()
    return redirect_to_today()  # /2025/7 のようなURLへリダイレクト

def redirect_to_today():
    """現在の日付を取得して、/年/月 にリダイレクト"""
    today = datetime.datetime.now()
    return redirect(url_for('calendar_page', year=today.year, month=today.month))


# ========================================
# 年・月指定のカレンダー表示ルート
# 例: /2025/7
# ========================================
@app.route('/<int:year>/<int:month>')
def calendar_page(year, month):
    """指定された年月のカレンダーを表示"""
    now = datetime.datetime.now()
    cal = calendar.Calendar(firstweekday=6)  # 日曜始まり
    month_days = cal.monthdayscalendar(year, month)

    # 前月計算
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    # 次月計算
    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_month = 1
        next_year += 1

    return render_template(
        'index.html',
        year=year,
        month=month,
        month_days=month_days,
        now=now,
        prev_year=prev_year,
        prev_month=prev_month,
        next_year=next_year,
        next_month=next_month
    )

# ========================================
# 種目設定ページ
# ========================================
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
    

    ordered_groups = get_grouped_exercises()
        
    return render_template(
        'exercises_edit.html',
        grouped_exercises=ordered_groups
    )

@app.route('/exercises/<int:exercise_id>', methods=['DELETE'])
def delete_exercise(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)

    # 該当の種目がログで使われているかを確認
    if WorkoutLog.query.filter_by(exercise_id=exercise.id).first():
        # 使用されていれば論理削除
        exercise.mark_as_deleted()
        db.session.commit()
        return jsonify({'status': 'logical delete'}), 200
    else:
        # 使用されていなければ物理削除
        db.session.delete(exercise)
        db.session.commit()
        return jsonify({'status': 'deleted'}), 200

@app.route("/exercises/reorder", methods=["POST"])
def reorder_exercises():
    data = request.get_json()
    for item in data:
        exercise = Exercise.query.get(item["id"])
        if exercise:
            exercise.order = item["order"]
    db.session.commit()
    return jsonify({"status": "ok"})


# ========================================
# 日付ごとの記録ページ
# ========================================
@app.route('/workout-log/<int:year>/<int:month>/<int:day>', methods=['GET', 'POST'])
def show_diary(year, month, day):
    try:
        date = datetime.date(year, month, day)
    except ValueError:
        return "Invalid date", 400

    if request.method == 'POST':
        date = datetime.date(year, month, day)

        exercise_ids = request.form.getlist('exercise_id')
        sets_list = request.form.getlist('sets')
        reps_list = request.form.getlist('reps')
        weight_list = request.form.getlist('weight')

        for i in range(len(exercise_ids)):
            if exercise_ids[i] and sets_list[i] and reps_list[i] and weight_list[i]:
                log = WorkoutLog(
                    date=date,
                    exercise_id=int(exercise_ids[i]),
                    sets=int(sets_list[i]),
                    reps=int(reps_list[i]),
                    weight=float(weight_list[i])
                )
                db.session.add(log)

        db.session.commit()
        return redirect(url_for('show_diary', year=year, month=month, day=day))

    # 表示時：登録済みのログと登録用の種目一覧
    logs = WorkoutLog.query.filter_by(date=date).all()

    ordered_groups = get_grouped_exercises()

    return render_template('training_log.html',
                           year=year, month=month, day=day,
                           logs=logs,
                           grouped_exercises=ordered_groups)

# ========================================
# WorkoutLog削除ルート
# ========================================
@app.route('/workout-log/<int:year>/<int:month>/<int:day>/delete', methods=['POST'])
def delete_log_for_date(year, month, day):
    log_id = request.form.get("log_id")
    if log_id:
        log = WorkoutLog.query.get(log_id)
        if log:
            db.session.delete(log)
            db.session.commit()
    # リダイレクト元ページへ戻る
    return redirect(url_for('show_diary', year=year, month=month, day=day))


# ========================================
# 実行
# ========================================
if __name__ == '__main__':
    app.run(port=5001, debug=True)