import os
import calendar
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_migrate import Migrate
from collections import defaultdict, OrderedDict
from sqlalchemy import func
from datetime import datetime, timedelta, date

from forms import PersonalInfoForm, LoginForm
from flask import session, flash
from models import db, Exercise, WorkoutLog , PersonalInfo

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
    if Exercise.query.count() == 0:
        current_user_id = session.get("user_id")
        if not current_user_id:
            return  # ログインしていない場合は登録をスキップ

        initial_exercises = [
            Exercise(name='アームカール', category='腕', detail='上腕二頭筋', order=0, user_id=current_user_id),
            Exercise(name='トライセプスエクステンション', category='腕', detail='上腕三頭筋', order=1, user_id=current_user_id),
            Exercise(name='ベンチプレス', category='胸', detail='大胸筋', order=0, user_id=current_user_id),
            Exercise(name='プッシュアップ', category='胸', detail='大胸筋', order=1, user_id=current_user_id),
            Exercise(name='ショルダープレス', category='肩', detail='三角筋', order=0, user_id=current_user_id),
            Exercise(name='サイドレイズ', category='肩', detail='三角筋側部', order=1, user_id=current_user_id),
            Exercise(name='ラットプルダウン', category='背中', detail='広背筋', order=0, user_id=current_user_id),
            Exercise(name='デッドリフト', category='背中', detail='脊柱起立筋', order=1, user_id=current_user_id),
            Exercise(name='スクワット', category='脚', detail='大腿四頭筋', order=0, user_id=current_user_id),
            Exercise(name='レッグカール', category='脚', detail='ハムストリングス', order=1, user_id=current_user_id),
            Exercise(name='グルートブリッジ', category='その他', detail='大臀筋', order=0, user_id=current_user_id),
            Exercise(name='ネックフレクション', category='その他', detail='頸部筋群', order=1, user_id=current_user_id)
        ]
        db.session.add_all(initial_exercises)
        db.session.commit()

# ================================================
# WorkoutLogのサンプルデータ挿入
# ================================================
def insert_sample_data():
    if WorkoutLog.query.count() == 0:   # 開発環境のみ使用
        current_user_id = session.get("user_id")
        if not current_user_id:
            return  # ログインしていない場合は登録をスキップ

        sample_logs = [
            WorkoutLog(date=date(2025, 7, 20), exercise_id=1, sets=3, reps=10, weight=40, user_id=current_user_id),
            WorkoutLog(date=date(2025, 7, 20), exercise_id=3, sets=3, reps=8, weight=60, user_id=current_user_id),
            WorkoutLog(date=date(2025, 7, 21), exercise_id=5, sets=4, reps=12, weight=20, user_id=current_user_id),
            WorkoutLog(date=date(2025, 7, 22), exercise_id=2, sets=3, reps=15, weight=15, user_id=current_user_id),
            WorkoutLog(date=date(2025, 7, 22), exercise_id=6, sets=2, reps=20, weight=10, user_id=current_user_id),
            WorkoutLog(date=date(2025, 7, 23), exercise_id=9, sets=5, reps=5, weight=80, user_id=current_user_id),
        ]
        db.session.add_all(sample_logs)
        db.session.commit()

# ==================================================
# ユーティリティ関数
# ==================================================
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

# ==================================================
# グラフデータ取得関数
# ==================================================
def get_chart_data(start_date, end_date):
    # クエリ: 日付・種目名・カテゴリごとに集計
    results = db.session.query(
        WorkoutLog.date,
        Exercise.name,
        Exercise.category,
        func.sum(WorkoutLog.sets * WorkoutLog.reps * WorkoutLog.weight).label('total_weight')
    ).join(Exercise)\
     .filter(WorkoutLog.date.between(start_date, end_date))\
     .group_by(WorkoutLog.date, Exercise.name, Exercise.category)\
     .order_by(WorkoutLog.date).all()

    # 日付ごと・種目名ごとに値を格納、種目名→カテゴリのマップも作成
    data_dict = defaultdict(lambda: defaultdict(float))
    category_map = {}
    for date_obj, exercise_name, category, total_weight in results:
        date_str = date_obj.strftime('%Y-%m-%d')
        data_dict[date_str][exercise_name] = total_weight
        category_map[exercise_name] = category

    labels = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((end_date - start_date).days + 1)]

    color_map = {
        '胸': '#ff6b6b',
        '肩': '#feca57',
        '腕': '#1dd1a1',
        '背中': '#54a0ff',
        '腹筋': '#a29bfe',
        '脚': '#ff9f43',
        'その他': '#dfe6e9'
    }

    # 種目名の一覧をカテゴリ順→名前順でソート
    category_order = ['胸', '肩', '腕', '背中', '腹筋', '脚', 'その他']
    sorted_exercise_names = []
    for cat in category_order:
        sorted_exercise_names.extend(sorted([name for name, c in category_map.items() if c == cat]))
    # Reverse the order for legend display
    sorted_exercise_names = list(reversed(sorted_exercise_names))
    datasets = []
    for name in sorted_exercise_names:
        values = [data_dict[dt].get(name, 0) for dt in labels]
        cat = category_map[name]
        datasets.append({
            'label': name,
            'data': values,
            'backgroundColor': color_map.get(cat, '#cccccc'),
            'borderColor': color_map.get(cat, '#cccccc'),
            'borderWidth': 1,
            'stack': 'stack1'
        })
    return labels, datasets

# ========================================
# トップページ "/" → 今日の年月へリダイレクト
# ========================================
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('start'))  # 未ログインなら start.html を表示

    insert_initial_data()
    insert_sample_data()
    return redirect_to_today()  # ログイン済みならカレンダー表示へ

def redirect_to_today():
    """現在の日付を取得して、/年/月 にリダイレクト"""
    today = datetime.now()
    return redirect(url_for('top_page', year=today.year, month=today.month))


# ========================================
# トップページ
# → 指定された年月のカレンダーを表示
# → 今日を含めた過去一週間のグラフを表示
# → 筋肉人形で部位ごとのトレーニング履歴を確認
# → 種目設定ページへのリンクを表示
# ========================================
@app.route('/<int:year>/<int:month>')
def top_page(year, month):
    """指定された年月のカレンダーを表示"""
    today = datetime.now()
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


    # ▼ グラフ用データ生成（過去7日分）
    end_date = today.date()
    start_date = end_date - timedelta(days=6)

    labels, datasets = get_chart_data(start_date, end_date)

    return render_template(
        'index.html',
        labels=labels,
        datasets=datasets,  # ← グラフデータを渡す
        reverse_legend=True,
        year=year,
        month=month,
        month_days=month_days,
        today=today,
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

    if request.method == 'POST':
        # クライアントから送られたJSONを取得して新しいExerciseを追加
        data = request.get_json()
        name = data.get('name')
        category = data.get('category')
        detail = data.get('detail')

        # 同じカテゴリ内での最大の並び順(order)を取得し、次の番号を設定
        max_order = db.session.query(db.func.max(Exercise.order)).filter_by(category=category).scalar() or 0
        new_ex = Exercise(name=name, category=category, detail=detail, order=max_order + 1, user_id=session.get("user_id"))

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
        date_obj = date(year, month, day)
    except ValueError:
        return "Invalid date", 400

    if request.method == 'POST':
        date_obj = date(year, month, day)

        exercise_ids = request.form.getlist('exercise_id')
        sets_list = request.form.getlist('sets')
        reps_list = request.form.getlist('reps')
        weight_list = request.form.getlist('weight')

        for i in range(len(exercise_ids)):
            if exercise_ids[i] and sets_list[i] and reps_list[i] and weight_list[i]:
                log = WorkoutLog(
                    date=date_obj,
                    exercise_id=int(exercise_ids[i]),
                    sets=int(sets_list[i]),
                    reps=int(reps_list[i]),
                    weight=float(weight_list[i]),
                    user_id=session.get("user_id")
                )
                db.session.add(log)

        db.session.commit()
        return redirect(url_for('show_diary', year=year, month=month, day=day))

    # 表示時：登録済みのログと登録用の種目一覧
    logs = WorkoutLog.query.filter_by(date=date_obj).all()

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
# ユーザー管理機能（ログイン・個人情報）
# ========================================

@app.route('/form', methods=["GET", "POST"])
def form():
    form = PersonalInfoForm()
    if form.validate_on_submit():
        new_person = PersonalInfo(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            height=form.height.data,
            weight=form.weight.data
        )
        db.session.add(new_person)
        db.session.commit()
        return redirect(url_for("user_info", user_id=new_person.id))
    return render_template("form.html", form=form)

@app.route('/user/<int:user_id>')
def user_info(user_id):
    user = PersonalInfo.query.get_or_404(user_id)
    return render_template("user_info.html", user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = PersonalInfo.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            session['user_id'] = user.id
            flash('ログイン成功', 'success')
            return redirect(url_for('mypage', user_id=user.id))
        else:
            flash('ユーザー名またはパスワードが間違っています', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("ログアウトしました", "info")
    return redirect(url_for('index'))

@app.route('/mypage')
def mypage():
    user_id = session.get('user_id')
    if not user_id:
        flash("ログインしてください")
        return redirect(url_for('login'))
    user = PersonalInfo.query.get(user_id)
    return render_template('user_info.html', user=user)

@app.route('/start')
def start():
    return render_template('start.html')


# ========================================
# 週別の合計重量をグラフ表示
# ========================================


# ========================================
# 筋肉部位ごとの直近1週間の合計重量を返すAPI
# ========================================
@app.route('/api/muscle-status')
def get_muscle_status():
    current_user_id = session.get("user_id")
    if not current_user_id:
        return jsonify({})  # 未ログインなら空データ

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)

    # カテゴリ別の合計重量を集計
    results = (
        db.session.query(
            Exercise.category,
            func.sum(WorkoutLog.sets * WorkoutLog.reps * WorkoutLog.weight).label("total_weight")
        )
        .select_from(WorkoutLog)
        .join(Exercise, WorkoutLog.exercise_id == Exercise.id)
        .filter(WorkoutLog.date.between(start_date, end_date))
        .filter(WorkoutLog.user_id == current_user_id)
        .group_by(Exercise.category)
        .all()
    )

    # カテゴリIDと紐づけ（SVG側と一致させる）
    category_id_map = {
        "胸": "chest",
        "肩": "shoulder",
        "腕": "arm",
        "背中": "back",
        "腹筋": "abs",
        "脚": "leg"
    }

    status = {}
    for category, total_weight in results:
        svg_id = category_id_map.get(category)
        if svg_id:
            status[svg_id] = total_weight

    return jsonify(status)


# ========================================
# 実行
# ========================================
if __name__ == '__main__':
    app.run(port=5001, debug=True)