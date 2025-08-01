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
# 指定カテゴリの種目一覧取得関数
# ==================================================
def get_exercises_by_category(category_name):
    """指定したカテゴリに属する種目一覧を取得"""
    exercises = Exercise.query.filter_by(
        category=category_name,
        is_deleted=False
    ).order_by(Exercise.order).all()
    return exercises

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
    exercise_to_category = {}
    for date_obj, exercise_name, category, total_weight in results:
        date_str = date_obj.strftime('%Y-%m-%d')
        data_dict[date_str][exercise_name] = total_weight
        category_map[exercise_name] = category
        exercise_to_category[exercise_name] = category

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
    return labels, datasets, category_map


# ========================================
# カテゴリ別直近2週間の合計重量を返すAPI
# ========================================
@app.route('/api/category-totals-14days')
def category_totals_14days():
    current_user_id = session.get("user_id")
    if not current_user_id:
        return jsonify({})

    user = PersonalInfo.query.get(current_user_id)
    multiplier = get_difficulty_multiplier(user)

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=13)

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

    # 100%基準の目標値
    base_targets = {
        "胸": 9000,
        "背中": 9000,
        "脚": 15000,
        "肩": 6000,
        "腕": 4000,
        "腹筋": 2000,
        "その他": 5000
    }

    # 難易度倍率と2週間分を反映
    targets = {k: v * multiplier * 2 for k, v in base_targets.items()}

    scores = {}
    for category, total in results:
        target = targets.get(category, 1)
        ratio = min(total / target * 100, 100)
        scores[category] = round(ratio)

    return jsonify(scores)


# ========================================
# トップページ "/" → 今日の年月へリダイレクト
# ========================================
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('start'))  # 未ログインなら start.html を表示

    insert_initial_data()
    insert_sample_data()
    return redirect_to_today()  # ログイン済みならトップページへ

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

    # ▼ 入力済み日をDBから取得
    user_id = session.get('user_id')
    start_date = date(year, month, 1)
    # 月末を求める
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    logs = WorkoutLog.query.filter(
        WorkoutLog.user_id == user_id,
        WorkoutLog.date >= start_date,
        WorkoutLog.date < end_date
    ).all()
    # 入力済み日をリスト化（文字列 or 数値どちらでもOK）
    filled_days = [log.date.day for log in logs]

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

    labels, datasets, category_map = get_chart_data(start_date, end_date)

    ordered_groups = get_grouped_exercises()

    return render_template(
        'index.html',
        labels=labels,
        datasets=datasets,  # ← グラフデータを渡す
        category_map=category_map,  # 種目のカテゴリマップを渡す
        reverse_legend=True,
        year=year,
        month=month,
        month_days=month_days,
        today=today,
        prev_year=prev_year,
        prev_month=prev_month,
        next_year=next_year,
        next_month=next_month,
        grouped_exercises=ordered_groups,
        filled_days=filled_days
    )

# ========================================
# 特定のカテゴリ（部位）の種目を表示するページ
# ========================================
@app.route('/category/<category_name>')
def show_category_exercises(category_name):
    current_user_id = session.get("user_id")

    # 英語 → 日本語カテゴリ変換マップ
    category_map = {
        'chest': '胸',
        'shoulder': '肩',
        'arm': '腕',
        'back': '背中',
        'abs': '腹筋',
        'leg': '脚',
        'other': 'その他'
    }

    jp_category = category_map.get(category_name)
    if not jp_category:
        return "カテゴリが見つかりません", 404

    exercises_in_category = Exercise.query.filter_by(
        category=jp_category,
        is_deleted=False,
        user_id=current_user_id
    ).order_by(Exercise.order).all()

    # Chart.js用のデータを取得（過去30日分）
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=29)

    results = db.session.query(
        WorkoutLog.date,
        func.sum(WorkoutLog.sets * WorkoutLog.reps * WorkoutLog.weight).label('total_weight')
    ).join(Exercise).filter(
        WorkoutLog.date.between(start_date, end_date),
        Exercise.category == jp_category,
        WorkoutLog.user_id == current_user_id
    ).group_by(WorkoutLog.date).order_by(WorkoutLog.date).all()

    labels = []
    values = []
    for single_date in (start_date + timedelta(n) for n in range(30)):
        labels.append(single_date.strftime('%Y-%m-%d'))
        matching = next((total for d, total in results if d == single_date), 0)
        values.append(matching if matching else 0)

    return render_template(
        'category_exercises.html',
        category_en=category_name,
        category_jp=jp_category,
        exercises=exercises_in_category,
        labels=labels,
        values=values
    )

def get_difficulty_multiplier(user: PersonalInfo):
    if not user:
        return 0.5  # ログインしていない場合などはデフォルト0.5

    # カスタム倍率またはプリセット倍率が設定されていればそれを返す
    if user.custom_number:
        return user.custom_number

    # custom_numberが未設定の場合、difficultyから決定（保険用）
    difficulty_map = {
        'beginner': 0.5,
        'intermediate': 0.75,
        'advanced': 1.0
    }
    return difficulty_map.get(user.difficulty, 0.5)  # 未設定なら0.5


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
        comment = request.form.getlist('comment')

        for i in range(len(exercise_ids)):
            if exercise_ids[i] and sets_list[i] and reps_list[i] and weight_list[i]and comment[i]:
                log = WorkoutLog(
                    date=date_obj,
                    exercise_id=int(exercise_ids[i]),
                    sets=int(sets_list[i]),
                    reps=int(reps_list[i]),
                    weight=float(weight_list[i]),
                    comment=comment[i],
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
@app.route('/form', methods=['GET', 'POST'])
def form_page():
    form = PersonalInfoForm()
    if form.validate_on_submit():
        # データベースに新規ユーザーを作成する処理
        user = PersonalInfo(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,  # ハッシュ化推奨
            height=form.height.data,
            weight=form.weight.data
        )
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        session['username'] = user.username

        return redirect(url_for('index'))  # トップページへ遷移

    # GETやバリデーション失敗時はフォームを表示
    return render_template('form.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = PersonalInfo.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            session['user_id'] = user.id
            flash('ログイン成功', 'success')
            return redirect(url_for('index', user_id=user.id))
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

    # user_info関数と同じロジックを追加
    bench = Exercise.query.filter_by(name='ベンチプレス').first()
    rift = Exercise.query.filter_by(name='デッドリフト').first()
    squat = Exercise.query.filter_by(name='スクワット').first()
    
    core_exercises = {
        'bench': bench,
        'rift': rift,
        'squat': squat
    }
    best_records = db.session.query(
        WorkoutLog.exercise_id,         # 種目ID
        Exercise.name,                  # 種目名
        func.max(WorkoutLog.weight)     # 最大重量
    ).join(Exercise).filter(
        WorkoutLog.user_id == user.id,      # 対象ユーザーのログのみ
        Exercise.is_deleted == False        # 削除されていない種目のみ
    ).group_by(
        WorkoutLog.exercise_id, Exercise.name
    ).all()

    best_weights = {ex_id: {'name': name, 'weight': weight} for ex_id, name, weight in best_records}
    
    # テンプレートにcore_exercisesを渡す
    return render_template(
    'user_info.html',
    user=user,
    core_exercises=core_exercises,
    best_weights=best_weights
)

@app.route('/start', methods=["GET", "POST"])
def start():
    register_form = PersonalInfoForm()
    login_form = LoginForm()
    return render_template("start.html", register_form=register_form, login_form=login_form)


@app.route('/user/<int:user_id>')
def user_info(user_id):
    # 1. ユーザー情報取得（存在しない場合は404）
    user = PersonalInfo.query.get_or_404(user_id)

    # 2. ベスト記録（種目ごとの最大重量）
    best_records = db.session.query(
        WorkoutLog.exercise_id,         # 種目ID
        Exercise.name,                  # 種目名
        func.max(WorkoutLog.weight)     # 最大重量
    ).join(Exercise).filter(
        WorkoutLog.user_id == user.id,      # 対象ユーザーのログのみ
        Exercise.is_deleted == False        # 削除されていない種目のみ
    ).group_by(
        WorkoutLog.exercise_id, Exercise.name
    ).all()

    # → {exercise_id: {'name': 種目名, 'weight': 最大重量}}
    best_weights = {ex_id: {'name': name, 'weight': weight} for ex_id, name, weight in best_records}

    bench = Exercise.query.filter_by(name='ベンチプレス').first()
    rift = Exercise.query.filter_by(name='デッドリフト').first()
    squat = Exercise.query.filter_by(name='スクワット').first()

    core_exercises = {
        'bench': bench,
        'rift': rift,
        'squat': squat
    }

    # 4. user_info.html にデータを渡す
    return render_template(
        'user_info.html',
        user=user,
        best_weights=best_weights,
        core_exercises=core_exercises
    )


# ========================================
# 週別のトレーニング記録を表示（グラフ、割合）
# ========================================
# 週の範囲を指定して記録を表示（例: /chart）
@app.route('/chart')
def weekly_data():
    today = datetime.now().date()
    sunday = today - timedelta(days=(today.weekday() + 1) % 7)  # 日曜始まり
    return redirect(url_for('weekly_report', week_range=f"{sunday.strftime('%Y-%m-%d')}~{(sunday + timedelta(days=6)).strftime('%Y-%m-%d')}"))

# 週の範囲を指定してグラフ表示（例: /chart/week/2025-07-27~2025-08-02）
@app.route('/weekly_report/<week_range>')
def weekly_report(week_range):
    try:
        # '2025-07-27~2025-08-02' 形式でパース
        start_str, end_str = week_range.split('~')
        start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
    except ValueError:
        return "Invalid week range format. Use YYYY-MM-DD~YYYY-MM-DD.", 400

    labels, datasets, category_map = get_chart_data(start_date, end_date)

    # カテゴリ別の合計重量を計算
    from collections import defaultdict
    category_totals = defaultdict(float)
    category_exercise_ratios = defaultdict(lambda: defaultdict(float))
    for dataset in datasets:
        exercise = dataset['label']
        category = category_map.get(exercise, 'その他')
        for value in dataset['data']:
            category_totals[category] += value
            category_exercise_ratios[category][exercise] += value

    # 表示順をカテゴリ順で固定
    category_order = ['胸', '肩', '腕', '背中', '腹筋', '脚', 'その他']
    ordered_category_totals = {cat: category_totals[cat] for cat in category_order if cat in category_totals}
    ordered_category_ratios = {cat: category_exercise_ratios[cat] for cat in category_order if cat in category_exercise_ratios}

    # 前週・次週のURL作成
    prev_start = (start_date - timedelta(weeks=1)).strftime('%Y-%m-%d')
    prev_end = (end_date - timedelta(weeks=1)).strftime('%Y-%m-%d')

    next_start_date = start_date + timedelta(weeks=1)
    next_end_date = end_date + timedelta(weeks=1)
    today = datetime.now().date()
    next_url = None
    if next_start_date <= today:
        next_url = url_for('weekly_report', week_range=f"{next_start_date.strftime('%Y-%m-%d')}~{next_end_date.strftime('%Y-%m-%d')}")

    return render_template(
        'weekly_report.html',
        labels=labels,
        datasets=datasets,
        category_map=category_map,
        reverse_legend=True,
        week_range=f"{start_date.strftime('%Y/%m/%d')}〜{end_date.strftime('%Y/%m/%d')}",
        prev_url=url_for('weekly_report', week_range=f"{prev_start}~{prev_end}"),
        next_url=next_url,
        category_totals=ordered_category_totals,
        category_exercise_ratios=ordered_category_ratios
    )

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
# 難易度選択画面
# ========================================
@app.route('/select')
def select():
    return render_template('select_level.html')

@app.route('/level', methods=['POST'])
def level():
    print("--- level関数が呼び出されました ---")
    difficulty = request.form.get('difficulty')
    custom_value = request.form.get('custom_value')
    print(f"受け取ったデータ: difficulty={difficulty}, custom_value={custom_value}")

    user_id = session.get('user_id')
    if not user_id:
        print("エラー: ユーザーがログインしていません")
        flash("ログインしてください")
        return redirect(url_for('login'))

    user = PersonalInfo.query.get(user_id)
    user.difficulty = difficulty

    # 難易度と倍率のマッピング
    level_map = {
        'beginner': 0.5,       # 初心者 → 基準値の50%
        'intermediate': 0.75,  # 中級者 → 基準値の75%
        'advanced': 1.0        # 上級者 → 基準値の100%
    }

    if difficulty in level_map:
        user.custom_number = level_map[difficulty]
    elif difficulty == 'custom' and custom_value:
        try:
            # カスタム倍率をfloatで設定
            user.custom_number = float(custom_value)
        except ValueError:
            user.custom_number = None
    else:
        user.custom_number = None

    print(f"ユーザーID {user_id} の difficulty を {user.difficulty} に、custom_number を {user.custom_number} に設定しました")

    db.session.commit()
    print("--- データベースにコミットが完了しました ---")

    flash(f"難易度: {difficulty}、倍率: {user.custom_number}", "success")
    return redirect(url_for('mypage'))


# ========================================
# 実行
# ========================================
if __name__ == '__main__':
    app.run(port=5010, debug=True)