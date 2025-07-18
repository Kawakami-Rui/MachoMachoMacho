import os
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_migrate import Migrate
import calendar
import datetime

from models import WorkoutLog  # モデルのインポート


app = Flask(__name__)

# ----------------------------------------
# トップページ "/" → 今日の年月へリダイレクト
# ----------------------------------------
@app.route('/')
def redirect_to_today():
    """現在の日付を取得して、/年/月 にリダイレクト"""
    today = datetime.datetime.now()
    return redirect(url_for('calendar_page', year=today.year, month=today.month))

# ----------------------------------------
# 年・月指定のカレンダー表示ルート
# 例: /2025/7
# ----------------------------------------
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

# ----------------------------------------
# 日付ごとの記録ページ
# ----------------------------------------
@app.route('/workout-log/<int:year>/<int:month>/<int:day>')
def show_diary(year, month, day):
    date_str = f"{year:04d}-{month:02d}-{day:02d}"
    items = [
        {"name": "apple", "value": 10},
        {"name": "banana", "value": 20},
        {"name": "cherry", "value": 30}
    ]
    return render_template('training_log.html', year=year, month=month, day=day, items=items)

# ----------------------------------------
# 実行
# ----------------------------------------
if __name__ == '__main__':
    app.run(port=5001, debug=True)