# example_script.py (新しいPythonファイル)

from app import app, db, Exercise # app.pyからapp, db, Exerciseをインポート

with app.app_context():
    # Exerciseテーブルから全ての種目を取得
    all_exercises = Exercise.query.all()

    # 取得した種目をループして内容を表示
    print("--- 全ての種目リスト ---")
    for ex in all_exercises:
        print(f"ID: {ex.id}, 名前: {ex.name}, カテゴリ: {ex.category}, 詳細: {ex.detail}, 削除済: {ex.is_deleted}")