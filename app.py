from flask import Flask, render_template, jsonify,request 
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
@app.route('/diary/<int:year>/<int:month>/<int:day>')
def show_diary(year, month, day):
    # URLから日付情報を取得し、文字列にフォーマット
    # 日付を 'YYYY-MM-DD' 形式にすることで、diary_entries のキーと一致させる
    date_str = f"{year:04d}-{month:02d}-{day:02d}"

    items = [
        {"name": "apple", "value": 10},
        {"name": "banana", "value": 20},
        {"name": "cherry", "value": 30}
    ]
    # テンプレートにデータを渡してレンダリング
    return render_template('static.html', year=year, month=month, day=day, items=items)

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """
    POSTリクエストを受けて負荷を計算し、結果をJSONで返す
    """
    default_value = 1
    data = request.json

    # JSONデータから値を取得。存在しない場合は空文字列
    weight_raw = data.get("weight", "")
    reps_raw = data.get("reps", "")
    sets_raw = data.get("sets", "")
    item_value_raw = data.get("itemValue", "")

    # すべての入力が空文字列の場合、負荷を0とする
    if weight_raw == "" and reps_raw == "" and sets_raw == "":
        return jsonify(result="現状約0.00kgの負荷です。"), 200

    try:
        # 入力が空文字列の場合はデフォルト値を使用、それ以外はfloatに変換
        weight = float(weight_raw) if weight_raw else default_value
        reps = float(reps_raw) if reps_raw else default_value
        sets = float(sets_raw) if sets_raw else default_value

        # 入力値が0以下の場合のエラーチェック
        if weight <= 0 or reps <= 0 or sets <= 0:
            return jsonify(result="正しい値を入力してください"), 400

        load = weight * reps * sets
        # item_value_raw が存在する場合のみ果物の情報を追加
        fruit_info = f"（果物の値: {item_value_raw}）" if item_value_raw else ""
        return jsonify(result=f"現状約{load:.2f}kgの負荷です。{fruit_info}"), 200
    except ValueError:
        # 数値変換エラーの場合
        return jsonify(result="数値を入力してください"), 400
# ==================================================
# 実行
# ==================================================
if __name__ == '__main__':
    app.run(port=5001, debug=True)