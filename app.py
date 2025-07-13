from flask import Flask , render_template

# ==================================================
# インスタンス生成
# ==================================================
app = Flask(__name__)

# ==================================================
# ルーティング
# ==================================================
@app.route('/')
def hello_world():
    return render_template('index.html')

from flask import Flask, render_template, request, redirect, url_for
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from collections import OrderedDict

app = Flask(__name__)

# 入力順を保持する曜日→体重の辞書（最大7件）
data = OrderedDict()

@app.route('/')
def input_page():
    return render_template('input.html')

@app.route('/submit', methods=['POST'])
def submit():
    day = request.form['day']
    weight = request.form['weight']

    if day and weight:
        weight = float(weight)

        # すでに同じ曜日があれば削除して順番更新
        if day in data:
            del data[day]

        # 上限7件を超えたら最古の曜日を削除
        if len(data) >= 7:
            data.popitem(last=False)

        # 新しい曜日を末尾に追加
        data[day] = weight

    return redirect(url_for('show_graph'))

@app.route('/graph')
def show_graph():
    if not data:
        return render_template('graph.html', graph=None)

    labels = list(data.keys())
    values = list(data.values())

    # グラフ生成
    fig, ax = plt.subplots()
    ax.plot(labels, values, marker='o')
    ax.set_title('dairy weight')
    ax.set_xlabel('day of week')
    ax.set_ylabel('weight')

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    graph = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return render_template('graph.html', graph=graph)

if __name__ == '__main__':
    app.run(debug=True)



# ==================================================
# 実行
# ==================================================
if __name__ == '__main__':
    app.run(port=5001, debug=True)