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
# データ送信・登録（同じ日付は上書き）
# ==================================================
@app.route('/submit', methods=['POST'])
def submit():
    from datetime import datetime, timedelta

    date = request.form['date']
    day = request.form['day']
    weight = float(request.form['weight'])
    height = float(request.form['height'])
    bmi = round(weight / ((height / 100) ** 2), 2) #round()は四捨五入するための機能。

    # 英語→日本語の曜日マップ。入力しなかった日が自動入力で曜日が英語で入力されるのを防ぐ。
    weekday_map = {
        'Mon': '月', 'Tue': '火', 'Wed': '水', 'Thu': '木',
        'Fri': '金', 'Sat': '土', 'Sun': '日'
    }

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # 最新日付の取得する。記録されていない日を新しく記録した日と最後に記録した日の差を求めて、記録0として保管する。
    c.execute('SELECT MAX(date) FROM bmi_records')
    latest_date_str = c.fetchone()[0]

    if latest_date_str:
        latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')
        new_date = datetime.strptime(date, '%Y-%m-%d')
        gap = (new_date - latest_date).days # 新しく記録した日付 - 最後に記録した日付

        if gap > 1: # 空いている日付の記録をすべて0.0にする。
            for i in range(1, gap):
                fill_date = latest_date + timedelta(days=i)
                fill_str = fill_date.strftime('%Y-%m-%d')
                fill_day_eng = fill_date.strftime('%a')
                fill_day = weekday_map[fill_day_eng]

                c.execute('''
                    INSERT INTO bmi_records (date, day, weight, height, bmi)
                    VALUES (?, ?, ?, ?, ?)
                ''', (fill_str, fill_day, 0.0, 0.0, 0.0))

    # 同じ日付は更新、それ以外は追加する。
    c.execute('SELECT id FROM bmi_records WHERE date = ?', (date,))
    existing = c.fetchone()

    if existing: # 更新
        c.execute('''
            UPDATE bmi_records
            SET day = ?, weight = ?, height = ?, bmi = ?
            WHERE date = ?
        ''', (day, weight, height, bmi, date))
    else: # 追加
        c.execute('''
            INSERT INTO bmi_records (date, day, weight, height, bmi)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, day, weight, height, bmi))

    conn.commit()
    conn.close()

    return redirect(url_for('show_graph'))


# ==================================================
# グラフ表示（最新7件）
# ==================================================
@app.route('/graph')
def show_graph():
    conn = sqlite3.connect(DATABASE) # データベースに接続。
    c = conn.cursor()
    c.execute('SELECT date, day, bmi FROM bmi_records ORDER BY date DESC LIMIT 7') # データベースの中の記録から最新の7件を取り出す。
    rows = c.fetchall()
    conn.close()

    if not rows:
        return render_template('graph.html', graph=None)

    rows.reverse()  # 古い順に並べ替ええる。

    # 月/日(曜日)形式でラベル作成する。
    from datetime import datetime
    labels = [
        f"{datetime.strptime(r[0], '%Y-%m-%d').strftime('%-m/%-d')}({r[1]})"
        for r in rows
    ]
    bmis = [r[2] for r in rows]

    fig, ax = plt.subplots()
    # ax.plot(labels, bmis, marker='o', color='blue', label='BMI')　#折れ線グラフを描画。
    ax.bar(labels, bmis, color='skyblue', label='BMI') # 棒グラフを描画。
    ax.set_title('最新7件のBMI推移（月/日・曜日）')
    ax.set_xlabel('日付（曜日）')
    ax.set_ylabel('BMI')
    ax.legend()

    buf = io.BytesIO()

    # matplotlibのFigureオブジェクト（fig）をPNG画像としてバッファに保存
    fig.savefig(buf, format='png')

    # バッファの読み出し位置を先頭に戻す（書き込んだ後は読み込み位置が末尾になっているため）
    buf.seek(0)

    # バッファから画像のバイナリデータを読み出して、Base64エンコードする
    # → HTMLの <img> タグで直接表示できるように文字列に変換
    graph = base64.b64encode(buf.read()).decode('utf-8')

    # バッファを閉じてメモリを解放（明示的にリソース解放）
    buf.close()

    # テンプレート graph.html を表示し、変数 graph にBase64文字列を渡す
    # HTML側では <img src="data:image/png;base64,{{ graph }}"> で画像を表示する
    return render_template('graph.html', graph=graph)

# ==================================================
# 記録一覧（削除リンク付き）
# ==================================================
@app.route('/records')
def view_records():
    conn = sqlite3.connect(DATABASE) # データベースに接続。
    c = conn.cursor() # オブジェクト作成。
    c.execute('SELECT id, date, day, weight, height, bmi FROM bmi_records ORDER BY date DESC') # データベースから項目別にデータを取得。
    records = c.fetchall() # リストに格納(タプルリスト)。
    conn.close()
    return render_template('records.html', records=records) # 変数 records をHTML側に渡すことで、HTMLで記録一覧をループ表示

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

#動作確認のみ。