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
            operationHeader.style.display = isEditing ? "none" : "flex";
        }

        // 各行の操作セル表示切替
        document.querySelectorAll(".operation-cell").forEach(cell => {
            cell.style.display = isEditing ? "none" : "flex";
        });

        // 各カテゴリの追加ボタン表示切替
        document.querySelectorAll(".add-button").forEach(btn => {
            btn.style.display = isEditing ? "none" : "block";
        });
    });

    // 追加ボタン処理
    document.querySelectorAll(".add-exercise-button").forEach(button => {
    button.addEventListener("click", () => {
        const category = button.dataset.category;
        const section = button.closest(".main-group-section");
        const exerciseList = section.querySelector(".exercise-list");

        if (exerciseList.querySelector(".input-row")) return;

        const inputRow = document.createElement("div");
        inputRow.className = "input-row";
        inputRow.innerHTML = `
            <div class="col part">${category}</div>
            <div class="col name"><input type="text" placeholder="種目名"></div>
            <div class="col detail"><input type="text" placeholder="詳細な筋肉部位"></div>
            <div class="col operation operation-cell">
                <button class="save">保存</button>
                <button class="cancel">取消</button>
            </div>
        `;
        exerciseList.insertBefore(inputRow, button.closest(".add-button"));

        // 取消ボタン
        inputRow.querySelector(".cancel").addEventListener("click", () => {
            inputRow.remove();
        });

        // 保存ボタン
        inputRow.querySelector(".save").addEventListener("click", async () => {
            const name = inputRow.querySelector("input[placeholder='種目名']").value.trim();
            const detail = inputRow.querySelector("input[placeholder='詳細な筋肉部位']").value.trim();

            inputRow.querySelector(".error-message")?.remove();

            if (!name) {
                const nameCol = inputRow.querySelector(".col.name");
                const error = document.createElement("div");
                error.className = "error-message";
                error.textContent = "※ 種目名は必須です";
                nameCol.appendChild(error);
                return;
            }

            exerciseList.querySelector(".no-entry")?.remove();

            const response = await fetch("/exercises", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, detail, category })
            });

            if (response.ok) {
                const result = await response.json();
                const newRow = document.createElement("div");
                newRow.className = "exercise-row";
                newRow.dataset.id = result.id;

                newRow.innerHTML = `
                    <div class="col part"></div>
                    <div class="col name">${result.name}</div>
                    <div class="col detail">${result.detail}</div>
                    <div class="col operation operation-cell">
                    <button class="move-up">↑</button>
                    <button class="move-down">↓</button>
                    <button class="delete">削除</button>
                    </div>
                `;

            exerciseList.insertBefore(newRow, inputRow);
            attachDeleteEvent(newRow.querySelector(".delete"));
            inputRow.remove();
            } else {
                alert("保存に失敗しました");
            }
        });
    });
});

// 削除ボタンのイベント付与
document.querySelectorAll(".delete").forEach(attachDeleteEvent);

    function attachDeleteEvent(button) {
        button.addEventListener("click", async function () {
            const row = this.closest("[data-id]");
            const exerciseId = row.dataset.id;
            const exerciseList = row.parentNode;

            if (!confirm("本当に削除しますか？")) return;

            const response = await fetch(`/exercises/${exerciseId}`, {
                method: "DELETE"
            });

            if (response.ok) {
                row.remove();

            // 残りがなければ「登録なし」を表示
            if (!exerciseList.querySelector("[data-id]")) {
                const noEntryRow = document.createElement("div");
                noEntryRow.className = "no-entry";
                noEntryRow.innerHTML = `
                    <div class="col part"></div>
                    <div class="col name">（登録なし）</div>
                    <div class="col detail"></div>
                    <div class="col operation"></div>
                `;
            exerciseList.insertBefore(noEntryRow, exerciseList.querySelector(".add-button"));
            }
            } else {
                alert("削除に失敗しました");
            }
        });
    }
});