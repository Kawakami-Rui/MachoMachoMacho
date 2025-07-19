// ページ読み込み後に初期化処理を実行
document.addEventListener("DOMContentLoaded", function () {
    // 編集モード切り替えボタンを取得
    const editButton = document.getElementById("edit-mode-toggle");
    if (!editButton) return;

    // 編集ボタンがクリックされたときの処理
    editButton.addEventListener("click", function () {
        const isEditing = this.dataset.editing === "true";
        this.dataset.editing = (!isEditing).toString();

        // 入力フォームがあればすべて削除
        document.querySelectorAll(".input-row").forEach(input => input.remove());

        // 操作列の表示・非表示切り替え
        const operationHeader = document.getElementById("operation-header");
        if (operationHeader) {
            operationHeader.style.display = isEditing ? "none" : "flex";
        }

        // 操作列の表示・非表示切り替え
        document.querySelectorAll(".operation-cell").forEach(cell => {
            cell.style.display = isEditing ? "none" : "flex";
        });

        // 操作列の表示・非表示切り替え
        document.querySelectorAll(".add-button-wrapper").forEach(btn => {
            btn.style.display = isEditing ? "none" : "block";
        });
    });

    // 「＋追加」ボタンが押されたときの処理
    document.querySelectorAll(".add-button-wrapper button").forEach(button => {
    button.addEventListener("click", () => {
        const category = button.dataset.category;
        const section = button.closest(".main-group-section");
        const exerciseList = section.querySelector(".exercise-list");

        if (exerciseList.querySelector(".input-row")) return;

        // 新しい種目入力用フォームを作成
        const inputRow = document.createElement("div");
        inputRow.className = "input-row";
        inputRow.innerHTML = `
            <div class="col part">${category}</div>
            <div class="col name">
                <input type="text" placeholder="種目名">
                <div class="error-message"></div>
            </div>
            <div class="col detail">
                <input type="text" placeholder="詳細な筋肉部位"></div>
            </div>
            <div class="col operation operation-cell">
                <button class="save button">保存</button>
                <button class="cancel button">取消</button>
            </div>
        `;
        exerciseList.insertBefore(inputRow, button.closest(".add-button-wrapper"));

        // 取消ボタンで入力フォームを削除
        inputRow.querySelector(".cancel.button").addEventListener("click", () => {
            inputRow.remove();
        });

        // 保存ボタンがクリックされたときの処理
        inputRow.querySelector(".save.button").addEventListener("click", async () => {
            const name = inputRow.querySelector("input[placeholder='種目名']").value.trim();
            const detail = inputRow.querySelector("input[placeholder='詳細な筋肉部位']").value.trim();

            const errorDiv = inputRow.querySelector(".error-message");
            errorDiv.style.display = "none";     // 初期化
            errorDiv.textContent = "";           // エラーメッセージをクリア

            // 種目名が空ならエラーを表示して終了
            if (!name) {
                errorDiv.textContent = "※ 種目名は必須です";
                errorDiv.style.display = "block";     // エラーメッセージを表示
                return;
            }



            // サーバーに保存成功した場合の処理
            const response = await fetch("/exercises", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, detail, category })
            });

            if (response.ok) {
                const result = await response.json();

                // 「登録なし」表示があれば削除
                const noEntry = exerciseList.querySelector(".no-entry");
                if (noEntry) {
                    noEntry.remove();
                }

                const newRow = document.createElement("div");
                newRow.className = "exercise-row";
                newRow.dataset.id = result.id;

                newRow.innerHTML = `
                    <div class="col part"></div>
                    <div class="col name">${result.name}</div>
                    <div class="col detail">${result.detail}</div>
                    <div class="col operation operation-cell">
                        <button class="move-up button">↑</button>
                        <button class="move-down button">↓</button>
                        <button class="delete button">削除</button>
                    </div>
                `;

                // 新しい種目行をDOMに挿入
                exerciseList.insertBefore(newRow, inputRow);
                // 全ての種目行にイベントを再登録
                document.querySelectorAll(".exercise-row").forEach(row => {
                    const deleteButton = row.querySelector(".delete button");
                    if (deleteButton) attachDeleteEvent(deleteButton);
                    attachMoveEvents(row);
                });
                inputRow.remove();
            } else {
                alert("保存に失敗しました");
            }
        });
    });
});

// 削除ボタンに処理を追加

    // 削除ボタンのイベント定義（確認→削除→「登録なし」表示）
    function attachDeleteEvent(button) {
        button.addEventListener("click", async function () {
            const row = this.closest("[data-id]");
            const exerciseId = row.dataset.id;
            const exerciseList = row.parentNode;

            // ダイアログで削除確認を出力
            if (!confirm("本当に削除しますか？")) return;

            const response = await fetch(`/exercises/${exerciseId}`, {
                method: "DELETE"
            });

            if (response.ok) {
                row.remove();

            // 他に種目が無ければ「登録なし」表示を追加
            if (!exerciseList.querySelector("[data-id]") &&
                !exerciseList.querySelector(".no-entry")) {
                const noEntryRow = document.createElement("div");
                noEntryRow.className = "no-entry";
                noEntryRow.innerHTML = `
                    <div class="col part"></div>
                    <div class="col name">（登録なし）</div>
                    <div class="col detail"></div>
                    <div class="col operation"></div>
                `;
                exerciseList.insertBefore(noEntryRow, exerciseList.querySelector(".add-button-wrapper"));
            }
            } else {
                alert("削除に失敗しました");
            }
        }, { once: true });
    }

// 並び替えボタンの処理を設定
function attachMoveEvents(row) {
    const upButton = row.querySelector(".move-up");
    const downButton = row.querySelector(".move-down");

    if (upButton) {
        upButton.addEventListener("click", () => {
            const prev = row.previousElementSibling;
            if (prev && prev.classList.contains("exercise-row")) {
                row.parentNode.insertBefore(row, prev);
                sendNewOrder(row.parentNode);
            }
        });
    }

    if (downButton) {
        downButton.addEventListener("click", () => {
            const next = row.nextElementSibling;
            if (next && next.classList.contains("exercise-row")) {
                row.parentNode.insertBefore(next, row);
                sendNewOrder(row.parentNode);
            }
        });
    }
}

// 並び順をサーバーに送信
function sendNewOrder(listElement) {
    const order = [];
    listElement.querySelectorAll(".exercise-row").forEach((row, index) => {
        order.push({
            id: row.dataset.id,
            order: index
        });
    });

        fetch("/exercises/reorder", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(order)
        }).catch(() => {
            alert("並び順の保存に失敗しました");
    });
}

    // ページ読み込み時にすべての行にイベントを追加
    document.querySelectorAll(".exercise-row").forEach(row => {
        const deleteButton = row.querySelector(".delete");
        if (deleteButton) attachDeleteEvent(deleteButton);
        attachMoveEvents(row);
    });
});