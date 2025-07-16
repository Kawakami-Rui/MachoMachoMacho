document.addEventListener("DOMContentLoaded", function () {
    const editButton = document.getElementById("edit-mode-toggle");

    if (!editButton) return;

    editButton.addEventListener("click", function () {
        const isEditing = this.dataset.editing === "true";
        this.dataset.editing = (!isEditing).toString();

        // 未保存の追加フォームを削除
        document.querySelectorAll(".input-row").forEach(input => input.remove());

        // 操作列（ヘッダ）
        const operationHeader = document.getElementById("operation-header");
        if (operationHeader) {
            operationHeader.style.display = isEditing ? "none" : "block";
        }

        // 各行の操作セル表示切替
        document.querySelectorAll(".operation-cell").forEach(cell => {
            cell.style.display = isEditing ? "none" : "flex";
        });

        // 各カテゴリの追加ボタン表示切替
        document.querySelectorAll(".add-button").forEach(btn => {
            btn.style.display = isEditing ? "none" : "block";
        });

        // 並び替えボタン ↑
        document.querySelectorAll(".move-up").forEach(button => {
            button.addEventListener("click", function () {
                const row = this.closest("[data-id]");
                const prev = row?.previousElementSibling;
                if (prev && prev.matches("[data-id]")) {
                    row.parentNode.insertBefore(row, prev);
                }
            });
        });

        // 並び替えボタン ↓
        document.querySelectorAll(".move-down").forEach(button => {
            button.addEventListener("click", function () {
                const row = this.closest("[data-id]");
                const next = row?.nextElementSibling;
                if (next && next.matches("[data-id]")) {
                    row.parentNode.insertBefore(next, row);
                }
            });
        });
    });

    // 各カテゴリごとの追加ボタン処理
    document.querySelectorAll(".add-exercise-button").forEach(button => {
        button.addEventListener("click", () => {
            const category = button.dataset.category;
            const section = button.closest(".main-group-section");
            const exerciseList = section.querySelector(".exercise-list");

            // 入力フォームが既に存在する場合は追加しない
            if (exerciseList.querySelector(".input-row")) return;

            const inputRow = document.createElement("div");
            inputRow.classList.add("input-row");
            inputRow.style.display = "flex";
            inputRow.style.padding = "4px 0";

            inputRow.innerHTML = `
                <div style="flex: 1;">${category}</div>
                <div style="flex: 1;"><input type="text" placeholder="種目名"></div>
                <div style="flex: 1;"><input type="text" placeholder="詳細な筋肉部位"></div>
                <div class="operation-cell" style="flex: 0 0 100px; display: flex; gap: 4px;">
                    <button class="save">保存</button>
                    <button class="cancel">取消</button>
                </div>
            `;

            exerciseList.insertBefore(inputRow, button.closest(".add-button"));

            // 取消処理
            inputRow.querySelector(".cancel").addEventListener("click", () => {
                inputRow.remove();
            });

            // 保存処理
            inputRow.querySelector(".save").addEventListener("click", async () => {
                const name = inputRow.querySelector("input[placeholder='種目名']").value.trim();
                const detail = inputRow.querySelector("input[placeholder='詳細な筋肉部位']").value.trim();

                // 既存のエラー表示があれば削除
                const existingError = inputRow.querySelector(".error-message");
                if (existingError) existingError.remove();

                // バリデーション：種目名は必須
                if (!name) {
                    const error = document.createElement("div");
                    error.classList.add("error-message");
                    error.style.color = "red";
                    error.style.fontSize = "0.9em";
                    error.style.marginTop = "4px";
                    error.textContent = "※ 種目名は必須です";

                    // 名前入力欄の直後に表示
                    const nameInput = inputRow.querySelector("input[placeholder='種目名']");
                    nameInput.parentNode.appendChild(error);

                    return;
                }

                // 保存成功後に「登録なし」を非表示にする
                const noEntry = exerciseList.querySelector(".no-entry");
                if (noEntry) noEntry.remove();

                // サーバーに保存リクエスト
                const response = await fetch("/exercises", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name, detail, category })
                });

                if (response.ok) {
                    const result = await response.json();
                    const newRow = document.createElement("div");
                    newRow.style.display = "flex";
                    newRow.style.padding = "4px 0";
                    newRow.dataset.id = result.id;

                    newRow.innerHTML = `
                        <div style="flex: 1;"></div>
                        <div style="flex: 1;">${result.name}</div>
                        <div style="flex: 1;">${result.detail}</div>
                        <div class="operation-cell" style="flex: 0 0 100px; display: flex; gap: 4px;">
                            <button class="move-up">↑</button>
                            <button class="move-down">↓</button>
                            <button class="delete">削除</button>
                        </div>
                    `;
                    exerciseList.insertBefore(newRow, inputRow);
                    attachDeleteEvent(newRow.querySelector(".delete")); // ✅ 新しく追加された行にも削除イベントを付ける
                    inputRow.remove();
                } else {
                    alert("保存に失敗しました");
                }
            });
        });
    });

    // 初期読み込み時の削除ボタンにイベント登録
    document.querySelectorAll(".delete").forEach(attachDeleteEvent);

    // 関数定義：削除ボタンの動作
    function attachDeleteEvent(button) {
        button.addEventListener("click", async function () {
            const row = this.closest("[data-id]");
            const exerciseId = row.dataset.id;

            

            if (!confirm("本当に削除しますか？")) return;

            const response = await fetch(`/exercises/${exerciseId}`, {
                method: "DELETE"
            });

            if (response.ok) {
                row.remove();
            } else {
                alert("削除に失敗しました");
            }

            // 削除成功後に「登録なし」を表示する（行がなくなった場合）
            const remaining = exerciseList.querySelectorAll("[data-id]");
            if (remaining.length === 0) {
                const noEntryRow = document.createElement("div");
                noEntryRow.classList.add("no-entry");
                noEntryRow.style.display = "flex";
                noEntryRow.style.padding = "4px 0";
                noEntryRow.style.fontStyle = "italic";
                noEntryRow.style.color = "#666";

                noEntryRow.innerHTML = `
                    <div style="flex: 1;"></div>
                    <div style="flex: 2;">（登録なし）</div>
                    <div style="flex: 0 0 100px;"></div>
                `;
                exerciseList.insertBefore(noEntryRow, exerciseList.querySelector(".add-button"));
            }
        });
    }
});
