document.addEventListener("DOMContentLoaded", () => {

    // ページ読み込み時に総負荷量を初期計算
    updateTotalLoad();

    // 各記録フォームに削除処理を追加
    document.querySelectorAll(".training-log-item form").forEach(form => {
        form.addEventListener("submit", async function (e) {
            e.preventDefault(); // デフォルトのフォーム送信をキャンセル

            // 削除確認ダイアログを表示
            if (!confirm("この記録を削除しますか？")) return;

            const formData = new FormData(this); // フォームデータを取得
            const action = this.action;          // フォームの送信先URLを取得

            // フェッチAPIで削除リクエストを送信
            const response = await fetch(action, {
                method: "POST",
                body: formData
            });

            if (response.ok) {
                // 成功時：該当記録をDOMから削除
                this.closest(".training-log-item").remove();

                // 総負荷量を再計算
                updateTotalLoad();

                // 記録が全て削除された場合、「まだ記録がありません」を表示
                if (document.querySelectorAll(".training-log-item").length === 0) {
                    const list = document.querySelector(".training-log-list");
                    const li = document.createElement("li");
                    li.className = "training-log-empty";
                    li.textContent = "まだ記録がありません";
                    list.appendChild(li);
                }
            } else {
                alert("削除に失敗しました");
            }
        });
    });

    // 総負荷量（セット数 × 回数 × 重量）を計算して表示
    function updateTotalLoad() {
        let total = 0;

        // 各記録アイテムを走査
        document.querySelectorAll(".training-log-item").forEach(item => {
            const textEl = item.querySelector(".log-item-text"); // 記録内容の要素を取得
            if (!textEl) return;

            const text = textEl.textContent;

            // 正規表現でセット数・回数・重量を抽出
            const match = text.match(/(\d+)\s*セット\s*\|\s*(\d+)\s*レップ\s*\|\s*(\d+\.?\d*)\s*kg/);

            if (match) {
                const sets = parseInt(match[1], 10);
                const reps = parseInt(match[2], 10);
                const weight = parseFloat(match[3]);
                total += sets * reps * weight; // 負荷量 = セット × 回数 × 重量
            }
        });

        // 計算結果を画面に表示
        const totalEl = document.getElementById("total-weight");
        if (totalEl) {
            totalEl.textContent = total.toFixed(1);
        }
    }
});
