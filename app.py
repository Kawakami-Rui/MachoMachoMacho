from flask import Flask, request, jsonify,render_template
from datetime import datetime


app = Flask(__name__)



@app.route("/")
def index():
    now = datetime.now() #datetimeはモジュールの機能。現在の日時を取得
    items = [
    {"name": "apple", "value": 10},
    {"name": "banana", "value": 20},
    {"name": "cherry", "value": 30}
    ]

    

    # テンプレートに月と日を渡す
    return render_template("static.html", month=now.month#その日の月　
                           ,day=now.day#その日の日
                           ,items =items
    )

@app.route("/api/calculate", methods=["POST"])
def calculate():
    default_value = 1
    data = request.json

    weight_raw = data.get("weight", "")
    reps_raw = data.get("reps", "")
    sets_raw = data.get("sets", "")
    item_value_raw = data.get("itemValue", "")  # ← 修正箇所

    try:
        weight = float(weight_raw) if weight_raw else default_value
        reps = float(reps_raw) if reps_raw else default_value
        sets = float(sets_raw) if sets_raw else default_value
        if weight <= 0 or reps <= 0 or sets <= 0:
            return jsonify(result="正しい値を入力してください")

        load = weight * reps * sets
        fruit_info = f"（果物の値: {item_value_raw}）" if item_value_raw else ""
    except ValueError:
        return jsonify(result="数値を入力してください"), 400

    if weight_raw == "" and reps_raw == "" and sets_raw == "":
        load = 0

    return jsonify(result=f"現状約{load:.2f}kgの負荷です。"), 200


if __name__ == "__main__":#実行。
    app.run(debug=True)