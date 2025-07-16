from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import sqlite3
import os
import japanize_matplotlib

app = Flask(__name__)
DATABASE = 'bmi.db'

# ==================================================
# DB初期化
# ==================================================
def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                day TEXT NOT NULL,
                weight REAL NOT NULL,
                reps REAL NOT NULL,
                sets REAL NOT NULL,
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
# データ送信・登録（同じ日付は上書き）
# ==================================================
@app.route('/submit', methods=['POST'])
def submit():
    from datetime import datetime, timedelta

    date = request.form['date']
    day = request.form['day']
    weight = float(request.form['weight'])
    reps = float(request.form['reps'])
    sets = float(request.form['sets'])
    bmi = weight * reps * sets 

    # 英語→日本語の曜日マップ
    weekday_map = {
        'Mon': '月', 'Tue': '火', 'Wed': '水', 'Thu': '木',
        'Fri': '金', 'Sat': '土', 'Sun': '日'
    }

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # 最新日付の取得
    c.execute('SELECT MAX(date) FROM bmi_records')
    latest_date_str = c.fetchone()[0]

    if latest_date_str:
        latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')
        new_date = datetime.strptime(date, '%Y-%m-%d')
        gap = (new_date - latest_date).days

        if gap > 1:
            for i in range(1, gap):
                fill_date = latest_date + timedelta(days=i)
                fill_str = fill_date.strftime('%Y-%m-%d')
                fill_day_eng = fill_date.strftime('%a')
                fill_day = weekday_map[fill_day_eng]

                c.execute('''
                    INSERT INTO bmi_records (date, day, weight, sets, reps, bmi)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (fill_str, fill_day, 0.0, 0.0, 0.0, 0.0))

    # 同じ日付は上書き、それ以外は挿入
    c.execute('SELECT id FROM bmi_records WHERE date = ?', (date,))
    existing = c.fetchone()

    if existing:
        c.execute('''
            UPDATE bmi_records
            SET day = ?, weight = ?, reps = ?, sets = ?, bmi = ? 
            WHERE date = ?
        ''', (day, weight, sets, reps, bmi, date))
    else:
        c.execute('''
            INSERT INTO bmi_records (date, day, weight, reps, sets, bmi)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (date, day, weight, sets, reps, bmi))

    conn.commit()
    conn.close()

    return redirect(url_for('show_graph'))


# ==================================================
# グラフ表示（最新7件）
# ==================================================
@app.route('/graph')
def show_graph():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT date, day, bmi FROM bmi_records ORDER BY date DESC LIMIT 7')
    rows = c.fetchall()
    conn.close()

    if not rows:
        return render_template('graph.html', graph=None)

    rows.reverse()  # 古い順に並べ替え

    # ✅ 月/日(曜日)形式でラベル作成
    from datetime import datetime
    labels = [
        f"{datetime.strptime(r[0], '%Y-%m-%d').strftime('%-m/%-d')}({r[1]})"
        for r in rows
    ]
    bmis = [r[2] for r in rows]

   # --- 修正箇所: fig, ax = plt.subplots() をここに移動 ---
    fig, ax = plt.subplots(figsize=(10, 6)) # グラフのサイズを調整すると見やすいかもしれません

    # 色が変わるしきい値を設定
    threshold = 2000 # 例: BMIが2000を超えたら色を変える (必要に応じて調整)
    threshold_2 = 3000

    for i, (label, bmi_value) in enumerate(zip(labels, bmis)):
        # 棒の幅
        bar_width = 0.8
        # 棒の中心X座標
        x_position = i # 各棒のX軸の位置

        if bmi_value <= threshold:
            # しきい値以下の場合は単一の色 (例: 青)
            ax.bar(x_position, bmi_value, width=bar_width, color='blue')
        else:
            if bmi_value <= threshold_2:
            # しきい値を超える場合は2つの棒を積み重ねる
            # しきい値までの部分 (例: 青)
                ax.bar(x_position, threshold, width=bar_width, color='blue')
            # しきい値を超えた部分 (例: 赤)
                ax.bar(x_position, bmi_value - threshold, width=bar_width, bottom=threshold, color='red')
            else:
                ax.bar(x_position, threshold, width=bar_width, color='blue')   
                ax.bar(x_position, bmi_value - threshold, width=bar_width, bottom=threshold, color='red')
                ax.bar(x_position,bmi_value - threshold_2,width=bar_width,bottom=threshold_2,color='green')

    # ラベルを正しく設定
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)

    # 凡例を手動で設定 (スタックバーの場合、自動生成が難しいので)
    # 凡例として表示したい色のダミープロットを作成
    ax.bar(0, 0, color='blue', label=f'BMI <= {threshold}') # ダミーの棒で凡例を作成
    ax.bar(0, 0, color='red', label=f'BMI > {threshold}') # ダミーの棒で凡例を作成
    
    # --- 修正ここまで ---

    ax.set_title('最新7件のBMI推移（月/日・曜日）')
    ax.set_xlabel('日付（曜日）')
    ax.set_ylabel('BMI')
    ax.legend()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    graph = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return render_template('graph.html', graph=graph)

# ==================================================
# 記録一覧（削除リンク付き）
# ==================================================
@app.route('/records')
def view_records():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT id, date, day, weight, sets, reps, bmi FROM bmi_records ORDER BY date DESC')
    records = c.fetchall()
    conn.close()
    return render_template('records.html', records=records)

# ==================================================
# 1件削除処理
# ==================================================
@app.route('/delete/<int:record_id>', methods=['POST'])
def delete_record(record_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM bmi_records WHERE id = ?', (record_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_records'))

# ==================================================
# アプリ起動
# ==================================================
if __name__ == '__main__':
    init_db()
    app.run(port=5001, debug=True)
