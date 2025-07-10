from flask import Flask , render_template
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
    # 現在の年と月を取得
    now = datetime.datetime.now()
    year = now.year
    month = now.month

    # カレンダーを作成
    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    return render_template('index.html', year=year, month=month, month_days=month_days, now=now)

# ==================================================
# 実行
# ==================================================
if __name__ == '__main__':
    app.run(port=5001, debug=True)