document.addEventListener("DOMContentLoaded", function () {
    const editToggle = document.getElementById("edit-mode-toggle");
    const orderButtons = document.querySelectorAll(".order-buttons");
    const addButtons = document.querySelectorAll(".add-button");

    editToggle.addEventListener("click", function () {
        orderButtons.forEach(btn => {
            btn.style.display = (btn.style.display === "none") ? "inline-block" : "none";
        });
        addButtons.forEach(btn => {
            btn.style.display = (btn.style.display === "none") ? "block" : "none";
        });
    });
    
    // 初期状態では編集モードをオフにする
    // 削除ボタン処理
    document.addEventListener("click", function(e) {
        if (e.target.classList.contains("delete-exercise")) {
            const row = e.target.closest("div[data-id]");
            const id = row.dataset.id;

            if (confirm("本当に削除しますか？")) {
                fetch(`/exercises/${id}`, { method: 'DELETE' })
                    .then(res => {
                        if (res.ok) {
                            row.remove();
                        } else {
                            alert("削除に失敗しました");
                        }
                    });
            }
        }
    });

 });