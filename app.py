from flask import Flask, render_template, request
import calendar
import datetime

# ==================================================
# インスタンス生成
# ==================================================
app = Flask(__name__)

# ==================================================
# ルーティング
# ==================================================
@app.route('/')
def index():
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

# ==================================================
# 実行
# ==================================================
if __name__ == '__main__':
    app.run(port=5001, debug=True)