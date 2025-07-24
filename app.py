from flask import Flask, render_template, request, flash
from forms import PersonalInfoForm
from flask import redirect, url_for
from models import db, PersonalInfo  # ← Exercise 使わないならこれはこれでOK
import calendar
import datetime
from forms import LoginForm  
from flask import session  # ログイン状態保持に使う


# ==================================================
# インスタンス生成
# ==================================================
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db' # SQLiteデータベースの場所指定
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 変更監視をオフ（パフォーマンス向上）
app.secret_key = 'your_secret_key'  # CSRF対策に必要
db.init_app(app)

#######forms.pyで定義したデータベースを作成！！　#######
with app.app_context():
    db.create_all()
##################################################


# ==================================================
# ルーティング
# ==================================================
@app.route('/')
def index():

    ###if文で、ログイン状態ならそのままカレンダー表示(index.html),未ログインなら新規登録、ログイン画面表示(start.html)。###
    if 'user_id' not in session:
        return render_template('start.html')  # 未ログインならstart.htmlへ

    """
    トップページのルーティング  
    GETリクエストで年と月を指定してカレンダーを表示
    クエリパラメータから年と月を取得し、カレンダーを生成する
    """
    # 現在の日付を取得
    now = datetime.datetime.now()

    # クエリパラメータから年と月を取得
    # 年と月が指定されていない場合は現在の年・月をデフォルト値として使用
    year = request.args.get('year', default=now.year, type=int)
    month = request.args.get('month', default=now.month, type=int)

    # 年と月の値が妥当かチェック
    cal = calendar.Calendar(firstweekday=6)  # 日曜始まりに設定
    month_days = cal.monthdayscalendar(year, month)

    # 前月の年・月を計算
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:  # 1月の前は前年の12月
        prev_month = 12
        prev_year -= 1

    # 次月の年・月を計算
    next_month = month + 1
    next_year = year
    if next_month == 13:  # 12月の次は翌年の1月
        next_month = 1
        next_year += 1

    # HTMLテンプレートに必要な変数を渡して描画
    return render_template(
        'index.html',
        year=year,               # 表示中の年
        month=month,             # 表示中の月
        month_days=month_days,   # 月ごとの日付リスト
        now=now,                 # 今日の日付（強調表示に使用）
        prev_year=prev_year,     # 前月の年
        prev_month=prev_month,   # 前月の月
        next_year=next_year,     # 次月の年
        next_month=next_month    # 次月の月
    )

####個人情報変更ページ###
@app.route('/form', methods=["GET", "POST"])
def form():
    form = PersonalInfoForm() ### forms.pyで定義したバリデータ"PersonalInfoForm"のインスタンスを作成 ###

    if form.validate_on_submit():
        new_person = PersonalInfo(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            height=form.height.data,
            weight=form.weight.data
        )
        db.session.add(new_person) # 上記のバリデータをクリアした場合、DBに追加予約(仮登録)
        db.session.commit()        # DBに確定保存
        ##flash("保存完了！", "success")## #flashで文字を一瞬表示させるコードだが、少し難しいため一時停止#
        return redirect(url_for("user_info", user_id=new_person.id))
    return render_template("form.html", form=form)

###個人情報閲覧ページ###
@app.route('/user/<int:user_id>')
def user_info(user_id):
    user = PersonalInfo.query.get_or_404(user_id)  # IDで検索。なければ404表示。
    return render_template("user_info.html", user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = PersonalInfo.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            session['user_id'] = user.id  # セッションに保存（ログイン状態）
            flash('ログイン成功', 'success')
            return redirect(url_for('user_info', user_id=user.id))
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
    user_id = session.get('user_id')  # ログイン状態なら保存されているuser_idを取り出す

    if not user_id:
        flash("ログインしてください")
        return redirect(url_for('login'))  # ログインしてなければログインページへ

    user = PersonalInfo.query.get(user_id)  # ログイン中のユーザー情報をDBから取得
    return render_template('user_info.html', user=user)  # ユーザー情報ページへ


@app.route('/start')
def start():
    return render_template('start.html')  # start.htmlを表示する



# ==================================================
# 実行
# ==================================================
if __name__ == '__main__':
    app.run(port=5002, debug=True)