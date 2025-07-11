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
    default_value = 1#全てのデフォルトの値
    data = request.json#jsonを読み込む
    #static.htmlでinoutされたものたちを呼び出す。
    weight_raw = data.get("weight", "")
    reps_raw = data.get("reps", "")
    sets_raw = data.get("sets", "")
    items_raw = data.get("items","")
    #それぞれの数が入っている場合にはfloatに入力。空ならdefault_valueを入力。
    try:
        weight = float(weight_raw) if weight_raw else default_value
        reps = float(reps_raw) if reps_raw else default_value
        sets = float(sets_raw) if sets_raw else default_value
        if weight <=0 or reps <= 0 or sets <= 0:
            return jsonify(result="正しい値を入力してください")
    
    #数字でない場合に怒る。
    except ValueError:
        return jsonify(result="数値を入力してください"), 400

    load = weight * reps * sets#運動負荷の計算
    "items"[items_raw] =load

    if weight_raw == "" and reps_raw == "" and sets_raw == "":#全部の値が空なら運動負荷に0を返す。
        load =0
    return jsonify(result=f"現状約{load:.2f}kgの負荷です。"),200#計算結果を参照し負荷を教える文を保存。
    

if __name__ == "__main__":#実行。
    app.run(debug=True)