from flask import Flask, render_template, request, redirect, url_for
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'bmi.db'

# ==================================================
# DB初期化関数
# ==================================================
def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

# ==================================================
# 入力ページ
# ==================================================
@app.route('/')
def input_page():
    return render_template('input.html')

# ==================================================
# 送信処理：DBに追加（履歴すべて残す）
# ==================================================
@app.route('/submit', methods=['POST'])
def submit():
    day = request.form['day']
    weight = float(request.form['weight'])
    height = float(request.form['height'])
    bmi = round(weight / ((height / 100) ** 2), 2)

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO bmi_records (day, weight, height, bmi)
        VALUES (?, ?, ?, ?)
    ''', (day, weight, height, bmi))
    conn.commit()
    conn.close()

    return redirect(url_for('show_graph'))

# ==================================================
# グラフ表示（最新7件を表示）
# ==================================================
@app.route('/graph')
def show_graph():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # 最新の7件を新しい順に取得 → 古い順に並び替え
    c.execute('SELECT day, bmi FROM bmi_records ORDER BY id DESC LIMIT 7')
    rows = c.fetchall()
    conn.close()

    if not rows:
        return render_template('graph.html', graph=None)

    rows.reverse()  # 古い順に並べる
    labels = [row[0] for row in rows]
    bmis = [row[1] for row in rows]

    fig, ax = plt.subplots()
    ax.plot(labels, bmis, marker='o', color='blue', label='BMI')
    ax.set_title('最新7件のBMI推移')
    ax.set_xlabel('曜日')
    ax.set_ylabel('BMI')
    ax.legend()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    graph = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return render_template('graph.html', graph=graph)

# ==================================================
# アプリ起動時にDB初期化
# ==================================================
if __name__ == '__main__':
    init_db()
    app.run(port=5001, debug=True)
